from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from src.domain.search_engine.Elastic_search.elastic_search import es 
# Define OCR and ASR routers
ocr_router = APIRouter()
asr_router = APIRouter()

# Define request models using BaseModel
class OCRRequest(BaseModel):
    ocr: str

class ASRRequest(BaseModel):
    asr: str

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
        topk=1000)
    
    # Process the OCR text and return a mock response
    return {"data":search_results}

# ASR route using APIRouter
@asr_router.post("/asr")
async def process_asr(request: ASRRequest):
    # Extract ASR text from the request body
    asr_text = request.asr
    if es.client:
        search_results = es.search_asr(
        index_name='asr_index',
        query=asr_text,
        topk=1000)
    # Process the OCR text and return a mock response
    return {"data":search_results}

