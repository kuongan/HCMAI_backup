from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os

search_api = APIRouter()

# Đọc file CSV khi ứng dụng FastAPI khởi động
csv_file = os.path.join('src', 'app','static','data','keyframe_info.csv')
data = pd.read_csv(csv_file)

# Định nghĩa mô hình dữ liệu cho payload
class SearchPayload(BaseModel):
    video_id: Optional[str] = None
    frame_id: Optional[int] = None  # frame_id là số nguyên

# Định nghĩa API để tìm kiếm dựa trên payload
@search_api.post("/search")
async def search_keyframes(payload: SearchPayload):
    filtered_data = data

    # Xử lý logic dựa trên payload
    if payload.video_id and payload.frame_id is not None:
        # Lọc theo video_id và tìm kiếm frame_id trong khoảng frame_id - 500 đến frame_id + 500
        filtered_data = filtered_data[
            (filtered_data['video_id'] == payload.video_id) & 
            (filtered_data['frame_id'].astype(int) >= payload.frame_id - 500) & 
            (filtered_data['frame_id'].astype(int) <= payload.frame_id + 500)
        ]
    elif payload.video_id:
        # Nếu chỉ nhập video_id
        filtered_data = filtered_data[filtered_data['video_id'] == payload.video_id]
    elif payload.frame_id is not None:
        # Nếu chỉ nhập frame_id
        filtered_data = filtered_data[filtered_data['frame_id'].astype(int) == payload.frame_id]

    # Chuyển frame_id thành dạng 3 chữ số
    filtered_data['frame_id'] = filtered_data['frame_id'].astype(str).apply(lambda x: x.zfill(3))

    return filtered_data.to_dict(orient="records")
