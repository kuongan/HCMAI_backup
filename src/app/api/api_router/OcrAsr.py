from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from src.domain.search_engine.Elastic_search.elastic_search import es 
import json 
# Define OCR and ASR routers
ocr_router = APIRouter()
asr_router = APIRouter()
# Define request models using BaseModel
class OCRRequest(BaseModel):
    ocr: str
    topk: int

class ASRRequest(BaseModel):
    asr: str
    topk: int

# Helper functions
def remove_duplicates(data_list):
    seen = set()
    result = []
    for item in data_list:
        # Convert dictionary to JSON string for comparison
        item_str = json.dumps(item, sort_keys=True)
        if item_str not in seen:
            seen.add(item_str)
            result.append(item)
    return result

def format_frame_ids(data_list):
    for item in data_list:
        if 'frame_id' in item:
            # Format frame_id to be at least 3 digits and overwrite the original value
            item['frame_id'] = f"{item['frame_id']:03}"
    return data_list

# OCR route using APIRouter
@ocr_router.post("/ocr")
async def process_ocr(request: OCRRequest):
    # Extract OCR text from the request body
    ocr_text = request.ocr
    print(ocr_text)
    if es.client:
        search_results = es.search_ocr(
            index_name='ocr_index',
            query=ocr_text,
            topk=request.topk
        )
    unique_results = remove_duplicates(search_results)
    formatted_results = format_frame_ids(unique_results)
    # Return formatted results
    return {"data": formatted_results}

# ASR route using APIRouter
@asr_router.post("/asr")
async def process_asr(request: ASRRequest):
    # Extract ASR text from the request body
    asr_text = request.asr
    if es.client:
        search_results = es.search_asr(
            index_name='asr_index',
            query=asr_text,
            topk=request.topk
        )
    unique_results = remove_duplicates(search_results)
    formatted_results = format_frame_ids(unique_results)
    # Return formatted results
    return {"data": formatted_results}