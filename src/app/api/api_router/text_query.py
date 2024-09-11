from typing import List, Dict
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.domain.information_extraction.feature_extractor import clip  
from src.domain.search_engine.vector_database import FaissDatabase
from src.common.query_processing import Translation, Text_Preprocessing
from langdetect import detect
from deep_translator import GoogleTranslator

# Define the router
side_bars = APIRouter()

# Define a Pydantic model to represent the data structure
class SidebarData(BaseModel):
    model: str
    textQuery: str

# Initialize the components
URL = []
faiss = FaissDatabase()
faiss.load_index('clip', r'src\app\static\data\faiss\clip.index')

# Initialize translation and text preprocessing
trans = Translation(from_lang='vi', to_lang='en', mode='google')
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

    # Detect the language of the text
    detected_lang = detect(data.textQuery)
    print(f"Detected language: {detected_lang}")

    # Translate if the detected language is Vietnamese
    if detected_lang == 'vi':
        print("Translating from Vietnamese to English...")
        translated_text = GoogleTranslator(source='vi', target='en').translate(data.textQuery)
        print(f"Translated text: {translated_text}")
    else:
        # If not Vietnamese, use the original text
        translated_text = data.textQuery

    # Preprocess the text
    preprocessed_text = text_preprocessor(translated_text)
    print(f"Preprocessed text: {preprocessed_text}")

    # Handle the query based on the model
    if data.model == 'Clip':
        query = preprocessed_text
        vector = clip.embed_query(query)
        result = faiss.search('clip', vector, 500)
        # Remove 'distances' from each dictionary in the result
        result = remove_distances(result)
    else:
        result = {"error": "Invalid model"}

    print(result)
    return JSONResponse(content={"data": result})
