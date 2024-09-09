from fastapi import APIRouter, requests
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import glob
import os

# Define the router
side_bars = APIRouter()

# Define a Pydantic model to represent the data structure
class SidebarData(BaseModel):
    model: str
    textQuery: str

URL = []

@side_bars.post('/')
def handle_sidebar_data(data: SidebarData):
    # You can access the data via the `data` variable
    print(f"Model: {data.model}")
    print(f"text_query: {data.textQuery}")
    # Return a response
    data_list = glob.glob(os.path.join('src', 'app', 'static', 'image', '**', '**', '*.jpg'), recursive=True)
    # List to store dictionaries
    result = []

    for file_path in data_list:
        # Extract the filename from the path (e.g., '597_L01_V001_start.jpg')
        filename = os.path.basename(file_path)
        
        # Split the filename by underscores and remove the '.jpg' extension
        parts = filename.replace('.jpg', '').split('_')
        
        # Create the dictionary if the format is correct (e.g., 597_L01_V001_start)
        if len(parts) == 4:
            frame_id = parts[0]   # '597'
            video_id = f"{parts[1]}_{parts[2]}"  # 'L01_V001'
            position = parts[3]   # 'start'

            # Add the extracted information into the dictionary
            result.append({
                'frame_id': frame_id,
                'video_id': video_id,
                'position': position
            })
    return JSONResponse(content={"data": result})