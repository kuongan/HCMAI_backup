from fastapi import APIRouter, HTTPException
import csv
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import os 
import random
# Khởi tạo APIRouter
router = APIRouter()

# Định nghĩa mô hình dữ liệu cho request body
class VideoFrameData(BaseModel):
    videoId: str
    frameId: str
    questionId: str
    qaType: Optional[str] = None  # Loại QA có thể không bắt buộc
    minFrameValue: Optional[int] = None  # Min frame
    maxFrameValue: Optional[int] = None  # Max frame
    Quantity: str
    randomNumber: int  # Số random phải có

class Small(BaseModel):
    questionId: str
    text: str
    qaType: Optional[str] = None

# Định nghĩa endpoint lưu dữ liệu CSV
@router.post("/save-csv")
async def save_csv(data: VideoFrameData):
    result = []
    VideoId = data.videoId
    frameId = data.frameId
    questionId = data.questionId
    qaType = data.qaType
    minFrameValue = data.minFrameValue
    maxFrameValue = data.maxFrameValue
    Quantity = data.Quantity
    randomNumber = data.randomNumber

    first = []

    if qaType == 'QA':
        first.append([VideoId, frameId, Quantity])
        questionId = f"query-p3-{questionId}-qa"
    else:
        first.append([VideoId, frameId])
        questionId = f"query-p3-{questionId}-kis"

    # Lặp qua số lần randomNumber và chọn frame ngẫu nhiên
    for _ in range(randomNumber):
        if qaType == 'QA':
            random_frame = random.randint(minFrameValue, maxFrameValue)
            result.append([VideoId, random_frame, Quantity])
        else:
            random_frame = random.randint(minFrameValue, maxFrameValue)
            result.append([VideoId, random_frame])

    # Tạo file CSV với tên là question_id.csv
    file_name = f"{questionId}.csv"

    # Kiểm tra nếu file đã tồn tại
    file_exists = os.path.isfile(file_name)
    if file_exists:
        with open(file_name,newline='') as f:
            r = csv.reader(f)
            data = [line for line in r]

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Ghi dữ liệu vào file mà không có header
        writer.writerows(first)
        if file_exists:
            writer.writerows(data)
        writer.writerows(result)

    return {"message": "CSV file saved successfully", "file_name": file_name}


@router.post("/save-csv-small")
async def save_csv_small(data: Small):
    questionId = data.questionId
    text = data.text.split(",")
    qaType = data.qaType
    if qaType == 'QA':
        questionId = f"query-p3-{questionId}-qa"
    else:
        questionId = f"query-p3-{questionId}-kis"
    # Tạo file CSV với tên là question_id.csv
    
    file_name = f"{questionId}.csv"

    # Kiểm tra nếu file đã tồn tại
    file_exists = os.path.isfile(file_name)

    result= ([text[0], text[1], text[2]] )if len(text) == 3 else  ([text[0], text[1]])
    with open(file_name,mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        # Ghi dữ liệu vào file mà không có header
        writer.writerow(result)