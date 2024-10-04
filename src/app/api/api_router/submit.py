from fastapi import APIRouter, HTTPException
import csv
import pandas as pd
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from src.app.api.api_router.date_filter import convert_urls
import os 
import random
# Khởi tạo APIRouter
router = APIRouter()
view_router = APIRouter()
FILE_DIRECTORY = 'result'

class Submit(BaseModel):
    imageUrls: List[str]
    frame_id: str
    video_id: str
    query_id: str
    rank: int
    answer: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    isQuestion: bool

class View(BaseModel):
    filename: str
    content: str
    
    
def initCSV(filename: str, data: Submit):
    parsed_urls = convert_urls(data.imageUrls)
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not filename.endswith('qa.csv'):
            for parsed_url in parsed_urls:
                writer.writerow([parsed_url['video_id'], parsed_url['frame_id']])
        else:
            for parsed_url in parsed_urls:
                writer.writerow([parsed_url['video_id'], parsed_url['frame_id'], data.answer])

def insert_data_at_position(data: Submit, csv_data: List[List[str]]):
    """Inserts data based on whether isQuestion is true or false."""
    pos = (data.rank - 1) * 5  # Calculate the insertion position
    
    if not data.isQuestion:
        # If isQuestion is False, insert only 5 rows (main frame + 4 random frames)
        main_entry = [data.video_id, data.frame_id]
        csv_data.insert(pos, main_entry)

        # Generate exactly 4 random frame_ids in the range [frame_id - 300, frame_id + 300]
        min_frame_id = max(int(data.frame_id) - 300, 1)
        max_frame_id = int(data.frame_id) + 300

        for i in range(1, 5):  # Ensure we only insert 4 random frames
            random_frame_id = random.randint(min_frame_id, max_frame_id)
            random_entry = [data.video_id, str(random_frame_id)]
            csv_data.insert(pos + i, random_entry)
    else:
        # If isQuestion is True, insert alternating answer variations
        main_entry = [data.video_id, data.frame_id, data.answer]
        csv_data.insert(pos, main_entry)

        # Alternating answer values around the main answer
        answer = int(data.answer)
        min_val, max_val = int(data.min), int(data.max)

        # Generate alternating decreasing and increasing values around the answer
        alternating_values = []
        for i in range(1, max_val - min_val + 1):
            if answer - i >= min_val:
                alternating_values.append(answer - i)
            if answer + i <= max_val:
                alternating_values.append(answer + i)
        
        # Insert the alternating values into the csv_data at the appropriate positions
        for i, val in enumerate(alternating_values):
            csv_data.insert(pos + i + 1, [data.video_id, data.frame_id, str(val)])

        # Fill up with random frame_ids, keeping the same answer value
        for _ in range(4):
            random_frame_id = random.randint(max(int(data.frame_id) - 300, 1), int(data.frame_id) + 300)
            random_entry = [data.video_id, str(random_frame_id), str(answer)]
            csv_data.insert(pos + 1 + len(alternating_values), random_entry)
    return csv_data


@router.post("/submit")
async def save_csv(data: Submit):
    try:
        # Ensure frame_id and video_id are provided
        if not data.frame_id or not data.video_id:
            raise HTTPException(status_code=400, detail="Missing videoId or frameId")
        print(data.isQuestion)
        # Generate file name
        filename = f'query-p3-{data.query_id}-{"qa" if data.isQuestion else "kis"}.csv'
        filecsv = os.path.join('result', filename)
        print(filecsv)
        # Read existing CSV data
        csv_data = []
        if not os.path.exists(filecsv):
            initCSV(filecsv, data)
        with open(filecsv, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            csv_data = list(reader)

        # Insert the new data at the desired position
        csv_data = insert_data_at_position(data, csv_data)

        # Write the updated data back to the CSV file
        with open(filecsv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)

        # Return success response
        return JSONResponse(status_code=200, content={"message": "CSV data saved successfully"})
  
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": f"Error saving CSV: {str(e)}"})

@view_router.get("/load")
async def load_file(filename: str):
    file_path = os.path.join(FILE_DIRECTORY, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Join each row with ', ' to ensure a single space between values
            content = '\n'.join([', '.join(row) for row in reader])  # Format as CSV-like text
        return {"content": content}
    else:
        raise HTTPException(status_code=404, detail="File not found")


@view_router.post("/save")
async def save_file(request: View):
    # Create the full file path
    file_path = os.path.join(FILE_DIRECTORY, request.filename)
    
    try:
        # Convert text content back to list of rows and split by lines and commas
        rows = [line.split(', ') for line in request.content.splitlines()]
        
        # Save the content to the specified file
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        return {"message": "File successfully saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
