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
    minQuantityValue: Optional[int] = None  # Min quantity
    maxQuantityValue: Optional[int] = None  # Max quantity
    randomNumber: int  # Số random phải có

class Small(BaseModel):
    questionId: str
    text: str

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
    minQuantityValue = data.minQuantityValue
    maxQuantityValue = data.maxQuantityValue
    randomNumber = data.randomNumber

    # Lặp qua số lần randomNumber và chọn frame ngẫu nhiên
    for _ in range(randomNumber):
        if qaType == 'QA':
            random_frame = random.randint(minFrameValue, maxFrameValue)
            number = random.randint(minQuantityValue, maxQuantityValue)
            result.append([VideoId, frameId, random_frame, number])
        else:
            random_frame = random.randint(minFrameValue, maxFrameValue)
            result.append([VideoId, frameId, random_frame])

    # Tạo file CSV với tên là question_id.csv
    file_name = f"{questionId}.csv"

    # Kiểm tra nếu file đã tồn tại
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        # Ghi dữ liệu vào file mà không có header
        writer.writerows(result)

    return {"message": "CSV file saved successfully", "file_name": file_name}


@router.post("/save-csv-small")
async def save_csv_small(data: Small):
    questionId = data.questionId
    text = data.text.split(",")
    # Tạo file CSV với tên là question_id.csv
    
    file_name = f"{questionId}.csv"

    # Kiểm tra nếu file đã tồn tại
    file_exists = os.path.isfile(file_name)

    result= ([text[0], text[1], text[2], text[3]] )if len(text) == 4 else  ([text[0], text[1], text[2]])
    with open(file_name,mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        # Ghi dữ liệu vào file mà không có header
        writer.writerow(result)