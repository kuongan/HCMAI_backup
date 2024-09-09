from __future__ import annotations

import json
import os
import re
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Tạo router cho các endpoint liên quan tới date
router = APIRouter()

# Đường dẫn tới thư mục chứa metadata JSON files
METADATA_FOLDER = r'src\app\static\metadata'


class DateFilterRequest(BaseModel):
    urls: list[str]  # This expects 'urls', not 'images'
    startDate: str | None = None
    endDate: str | None = None


def parse_url(url: str) -> dict | None:
    parts = url.split('/')
    filename = parts[-1]

    # Sử dụng regex để lấy các thành phần
    match = re.match(r'(\d+)_L01_V(\d+)_([a-z]+)\.jpg', filename)
    if match:
        frame_id = match.group(1)
        video_id = f'L01_V{match.group(2)}'
        position = match.group(3)
        return {
            'frame_id': frame_id,
            'video_id': video_id,
            'position': position,
        }
    return None


def convert_urls(urls: list[str]) -> list[dict | None]:
    return [
        parse_url(url) for url in urls
        if parse_url(url) is not None
    ]


def checkdate(date_str: str, start_date: str, end_date: str) -> bool:
    publish_date = datetime.strptime(date_str, '%d/%m/%Y')
    start_date_cleaned = start_date.split('T')[0]
    end_date_cleaned = end_date.split('T')[0]

    start_date_obj = datetime.strptime(start_date_cleaned, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date_cleaned, '%Y-%m-%d')

    return start_date_obj <= publish_date <= end_date_obj


def split(url: str) -> str | None:
    """Tách tên thư mục từ URL."""
    parts = url.split('/')
    if len(parts) > 5:
        return parts[6]
    return None


@router.post('/date')
async def filter_by_date(request: DateFilterRequest):
    valid_urls = []

    # Lặp qua tất cả các URL
    for url in request.urls:
        video_id = split(url)
        if video_id is None:
            continue

        json_file = os.path.join(METADATA_FOLDER, f'{video_id}.json')
        if not os.path.exists(json_file):
            continue

        with open(json_file, encoding='utf-8') as file:
            metadata = json.load(file)

        publish_date = metadata.get('publish_date')

        if publish_date and request.startDate and request.endDate:
            if checkdate(
                publish_date,
                request.startDate,
                request.endDate,
            ):
                valid_urls.append(url)

    urls = convert_urls(valid_urls)
    return JSONResponse(
        content={'data': urls},
        status_code=200,
    )
