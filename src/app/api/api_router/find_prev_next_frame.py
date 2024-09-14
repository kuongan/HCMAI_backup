from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import json
import os

# Đường dẫn tới thư mục chứa metadata JSON files
DATA_FOLDER = os.path.join('src','app','static','data')

# Define the request model
class ImageURL(BaseModel):
    url: str

# Create router for the endpoint
router = APIRouter()

@router.post('/find_prev_next_frame')
def find_prev_next_frame(data: ImageURL):
    parts = data.url.split('/')
    current_uri = parts[-1]

    uri_to_index_path = os.path.join(DATA_FOLDER, 'uri_to_index.json')
    index_to_uri_path = os.path.join(DATA_FOLDER, 'index_to_uri.json')
    
    # Load uri_to_index.json
    with open(uri_to_index_path, 'r') as file:
        uri_to_index = json.load(file)
    
    left_index = uri_to_index[current_uri] - 1
    right_index = uri_to_index[current_uri] + 1
    if left_index < 0:
        left_index = 0
    if right_index >= len(uri_to_index):
        right_index = len(uri_to_index) - 1

    # Load index_to_uri.json
    with open(index_to_uri_path, 'r') as file:
        index_to_uri = json.load(file)
    left_uri = index_to_uri[str(left_index)]
    right_uri = index_to_uri[str(right_index)]
    
    def add_http_prefix(uri):
        parts = uri.split("_")
        base = f"http://localhost:8000/static/image/Videos_{parts[1]}/{parts[1]}_{parts[2]}/{uri}"
        return base
    
    left_uri = add_http_prefix(left_uri)
    right_uri = add_http_prefix(right_uri)
    
    return JSONResponse(
        content={
            'prev': left_uri, 
            'next': right_uri
        },
        status_code=200,
    )