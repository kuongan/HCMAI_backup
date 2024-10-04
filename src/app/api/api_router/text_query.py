from typing import List, Dict
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.domain.information_extraction.feature_extractor import clip
from src.domain.search_engine.vector_database import FaissDatabase
from src.common.query_processing import Translation, Text_Preprocessing
from langdetect import detect
from googletrans import Translator

import time

# Define the router
side_bars = APIRouter()

# Define a Pydantic model to represent the data structure
class SidebarData(BaseModel):
    model: str
    textQuery: str
    topK: str

# Initialize the components
URL = []
faiss = FaissDatabase()

faiss.load_index('clip', r'src/app/static/data/faiss/clip.index')

# Initialize translation and text preprocessing
GGtranslator = Translator() #Google Trans

text_preprocessor = Text_Preprocessing()

def remove_distances(result: List[Dict]) -> List[Dict]:
    """Remove 'distances' field from each dictionary in the result list."""
    cleaned_result = []
    for item in result:
        cleaned_item = {k: v for k, v in item.items() if k != 'distance'}
        cleaned_result.append(cleaned_item)
    return cleaned_result

@side_bars.post('/')
def handle_sidebar_data(data: SidebarData):
    # You can access the data via the `data` variable
    print(f"Model: {data.model}")
    print(f"text_query: {data.textQuery}")
    print(f"topK: {data.topK}")

    start = time.time() 
    # Detect the language of the text
    detected_lang = detect(data.textQuery)
    print(f"Detected language: {detected_lang}")

    # Translate if the detected language is Vietnamese
    detectTime = time.time() 
    if detected_lang == 'vi':
        print("Translating from Vietnamese to English...")
        # translated_text = GoogleTranslator(source='vi', target='en').translate(data.textQuery)
        translated_text = GGtranslator.translate(str(data.textQuery), src="vi", dest="en").text
        print(f"Translated text: {translated_text}")
    else:
        # If not Vietnamese, use the original text
        translated_text = data.textQuery

    # Preprocess the text
    translateTime = time.time() 
    preprocessed_text = text_preprocessor(translated_text)
    print(f"Preprocessed text: {preprocessed_text}")
    preprocessingTime = time.time() 

    # Handle the query based on the model
    if data.model == 'Clip': ## Blip Clip Beit3
        query = preprocessed_text
        vector = clip.embed_query(query)
        result = faiss.search('clip', vector, int(data.topK))
        # Remove 'distances' from each dictionary in the result
        result = remove_distances(result)
    else:
        result = {"error": "Invalid model"}
    queryTime = time.time() 

    print('Detect Language Time:',detectTime - start)
    print('Translate Time:', translateTime - detectTime)
    print('Preprocessing Time:', preprocessingTime - translateTime)
    print('Query Time:', queryTime - preprocessingTime)

    return JSONResponse(content={"data": result})
