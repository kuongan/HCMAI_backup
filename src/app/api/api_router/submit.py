from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import json
import requests
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
# Khởi tạo APIRouter
router = APIRouter()

# Constants for API base path
MAP_KEYFRAMES_FOLDER = os.path.join('src', 'app', 'static', 'map-keyframes')
BASE_URL = "https://eventretrieval.one/api/v2"
USERNAME = "team56"
PASSWORD = "Q3tYU2A7nk"
# EVALUATION_ID = "69ec2262-d829-4ac1-94a2-1aa0a6693266"
EVALUATION_ID = "bec3b699-bdea-4f2c-94ae-61ee065fa76e"  
SECTION_ID = "YC55L7LQwbqJYIbYvyMcKtaX9a9ZfyEP"

# Định nghĩa mô hình dữ liệu cho request body
class VideoFrameData(BaseModel):
    videoId: str
    frameId: str
    qa: str

# Step 1: Login to get sessionID
class LoginRequest(BaseModel):
    username: str
    password: str

# Step 3: Submit an answer (for QA or KIS task)
class AnswerSet(BaseModel):
    mediaItemName: Optional[str] = None  # For KIS task
    text: Optional[str] = None           # For QA task
    start: Optional[int] = None          # Start time for KIS
    end: Optional[int] = None            # End time for KIS

class Submission(BaseModel):
    answerSets: List[AnswerSet]

class LoginResponse(BaseModel):
    id: str
    username: str
    role: str
    sessionId: str

# Chuyển đổi từ frameId sang giây, tùy thuộc và loại câu hỏi là QA hay KIS
def convert_to_time(data = VideoFrameData): 
        #Lấy URL từ file json
    mapkeyframes_file = os.path.join(MAP_KEYFRAMES_FOLDER, f'{data.videoId}.csv')
    #Lấy fps từ file csv
    csv_file = pd.read_csv(mapkeyframes_file)
    fps = csv_file.loc[0,'fps'] 
    return int(int(data.frameId)/fps*1000)

# Tạo file json đáp án cho từng loại câu hỏi
def save_json(data: VideoFrameData):
    # Tạo file JSON từ dữ liệu truyền vào
    if (data.qa != "No-data"): 
        frame_millisecond = convert_to_time(data)
        json_data = {
            "answerSets": [
                {
                "answers": [
                    {
                    "text": f"{data.qa}-{data.videoId}-{frame_millisecond}"
                    }
                ]
                }
            ]
            }
    else: 
        frame_millisecond = convert_to_time(data)
        json_data = {
            "answerSets": [
                {
                "answers": [
                    {
                    "mediaItemName": data.videoId,
                    "start": frame_millisecond,
                    "end": frame_millisecond
                    }
                ]
                }
            ]
            }
    
    # Lưu file JSON
    with open("submission_data.json", "w") as json_file:
        json.dump(json_data, json_file)
    return json_data  # Trả về JSON đã tạo

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    url = f"{BASE_URL}/login"
    try:
        response = requests.post(url, json=request.dict())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=f"Login failed: {str(e)}")

# Step 2: Retrieve evaluation ID
@router.get("/evaluations")
def get_evaluation_list(session_id: str):
    url = f"{BASE_URL}/client/evaluation/list"
    headers = {"Authorization": session_id}
    try:
        response = requests.get(url, headers=headers, params={"session": session_id})
        response.raise_for_status()
        evaluations = response.json()
        # Filter for active evaluations
        active_evaluations = [eval for eval in evaluations if eval['status'] == "ACTIVE"]
        return active_evaluations
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch evaluations: {str(e)}")

@router.post("/submit")
def submit_answer(evaluation_id: str, session_id: str, submission):
    url = f"{BASE_URL}/submit/{evaluation_id}"
    headers = {"Authorization": session_id,  "Content-Type": "application/json"}
    try:
        print(type(submission))
        print(url)
        response = requests.post(url, json=submission, params={"session": session_id}, headers=headers)
        print(response)
        response.raise_for_status()
        return {"message": "Submission successful", "response": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Submission failed: {str(e)}")
    
# Example endpoint to use login, get evaluations, and submit in sequence
@router.post("/submit-answer")
def submit_full_process(data: VideoFrameData):
    print(data)
    submission = save_json(data)
    print(submission)
    # Step 3: Submit the answer
    return submit_answer(EVALUATION_ID, SECTION_ID, submission)