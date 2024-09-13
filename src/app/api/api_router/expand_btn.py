from __future__ import annotations

import json
import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Tạo router cho các endpoint liên quan tới date
router = APIRouter()

# Đường dẫn tới thư mục chứa metadata JSON files
METADATA_FOLDER = os.path.join('src','app','static','metadata')

class imageURL(BaseModel):
    url: str  # This expects 'urls', not 'images'

@router.post('/expandBtn')
async def filter_by_date(request: imageURL):
    print(request.url)
    parts = request.url.split('/')

    # Lấy phần chứa 'L08_V018' và '19374'
    video_id = parts[6]  # 'L08_V018'
    frame_id = parts[7].split('_')[0]
    print(video_id, frame_id)

    json_file = os.path.join(METADATA_FOLDER, f'{video_id}.json')

    with open(json_file, encoding='utf-8') as file:
        metadata = json.load(file)

    video_url = metadata.get('watch_url')

    return JSONResponse(
        content={
            'frameId': frame_id, 
            'videoURL': video_url,
            'videoId': video_id
        },
        status_code=200,
    )
