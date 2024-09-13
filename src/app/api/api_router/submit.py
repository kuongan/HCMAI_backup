from fastapi import APIRouter, Request, HTTPException
import csv
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Khởi tạo APIRouter
router = APIRouter()

# Định nghĩa mô hình dữ liệu cho request body
class VideoFrameData(BaseModel):
    videoId: str
    frameId: str

# Định nghĩa endpoint lưu dữ liệu CSV
@router.post("/save-csv")
async def save_csv(data: VideoFrameData):
    try:
        # Đảm bảo dữ liệu không trống
        if not data.videoId or not data.frameId:
            raise HTTPException(status_code=400, detail="Missing videoId or frameId")

        # Mở file CSV để append dữ liệu mới
        with open("data.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([data.videoId, data.frameId])  # Lưu dòng mới vào CSV

        # Trả về phản hồi JSON khi thành công
        return JSONResponse(status_code=200, content={"message": "CSV data saved successfully"})

    except Exception as e:
        # Xử lý lỗi và trả về phản hồi
        return JSONResponse(status_code=500, content={"message": f"Error saving CSV: {str(e)}"})
