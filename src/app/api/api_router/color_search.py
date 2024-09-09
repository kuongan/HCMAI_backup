from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.domain.search_engine.Elastic_search.elastic_search import es
from fastapi.responses import JSONResponse


# Initialize router
router = APIRouter()
COLOR_MAP = {
    "rgb(0, 0, 0)": "black",
    "rgb(0, 0, 255)": "blue",
    "rgb(165, 42, 42)": "brown",
    "rgb(0, 128, 0)": "green",
    "rgb(128, 128, 128)": "grey",
    "rgb(255, 165, 0)": "orange",
    "rgb(255, 192, 203)": "pink",
    "rgb(128, 0, 128)": "purple",
    "rgb(255, 0, 0)": "red",
    "rgb(255, 255, 255)": "white",
    "rgb(255, 255, 0)": "yellow"
}

# Helper function to convert RGB value to color name
def rgb_to_color_name(rgb_value: str) -> str:
    return COLOR_MAP.get(rgb_value, rgb_value)  # Default to RGB if not found

# Model to represent bounding box information
class BoundingBox(BaseModel):
    row: int  # Starting row index of the box (0-based)
    col: str  # Starting column index of the box ('a'-based)
    rows_covered: int  # Number of rows the box spans
    cols_covered: int  # Number of columns the box spans
    color: str  # Color of the box

# Helper function to convert column letter ('a'-'g') to index
def column_letter_to_index(letter: str) -> int:
    return ord(letter.lower()) - ord('a')

# Helper function to convert index back to a column letter ('a'-'g')
def column_index_to_letter(index: int) -> str:
    return chr(ord('a') + index)

# Route to encode multiple bounding boxes into grid positions and send to Elasticsearch
@router.post("/encode_box/")
async def encode_box(boxes: List[BoundingBox]):
    encoded_positions = []

    for bbox in boxes:
        # Calculate grid positions based on the number of rows and columns the box covers
        for r in range(bbox.row, bbox.row + bbox.rows_covered):
            for c in range(column_letter_to_index(bbox.col), column_letter_to_index(bbox.col) + bbox.cols_covered):
                col_letter = column_index_to_letter(c)
                bbox.color = rgb_to_color_name(bbox.color)
                # Encode the position as row, column, and color
                encoded_positions.append(f"{r}{col_letter}{bbox.color}")
    
    # Sort encoded positions lexicographically (row first, then column)
    encoded_positions.sort()

    # Join sorted encoded positions into a string
    encoded_string = " ".join(encoded_positions)
    print(encoded_string)    
    if es.client:
        search_results = es.search_color(
            index_name='color_index',
            query=encoded_string,
            topk=500,
        )
        # Assuming search_results is a list of dictionaries with frame_id, video_id, and position
        return JSONResponse(content={"data": search_results})

    raise HTTPException(status_code=404, detail="Elasticsearch client not available")