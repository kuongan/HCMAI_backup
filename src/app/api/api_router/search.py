from fastapi import APIRouter, Body
from typing import Dict

search_api = APIRouter()

@search_api.post("")
async def search(text: Dict[str, str] = Body(...)):
    text_value = text.get('text')
    if not text_value:
        return {"error": "No text provided"}

    # Construct the URL (assuming static files are served correctly)
    url = f"static/image/{text_value}.jpg"
    return {"url": url}
