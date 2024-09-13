from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import os
from src.app.api.api_router.date_filter import router as date_router
from src.app.api.api_router.text_query import side_bars
from src.app.api.api_router.searchtop import search_api
from src.app.api.api_router.color_search import router as color_router
from src.app.api.api_router.object import router as od_router
from src.app.api.api_router.OcrAsr import ocr_router 
from src.app.api.api_router.OcrAsr import asr_router 
from src.app.api.api_router.rerank import router as rerank_router
from src.app.api.api_router.expand_btn import router as expandBtn_router
from src.app.api.api_router.submit import router as submit_router
# Define the base directory for the app folder
BASE_DIR = Path(__file__).resolve().parent

# Create the FastAPI app instance
app = FastAPI()

# Mount static files (CSS, JS, images)
static_dir = Path(BASE_DIR, "static")
print(f"Static files directory: {static_dir}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure the Jinja2 templates directory
templates_dir = Path(BASE_DIR, "templates")
print(f"Templates directory: {templates_dir}")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the homepage with template."""
    return templates.TemplateResponse("index.html", {"request": request})
# Include the router for image routes
app.include_router(date_router)
app.include_router(color_router)
app.include_router(od_router)
app.include_router(ocr_router)
app.include_router(asr_router)
app.include_router(rerank_router)
app.include_router(expandBtn_router)
app.include_router(submit_router)
app.include_router(search_api)
app.include_router(side_bars, prefix="/side-bar")


# uvicorn src.app.main:app --reload instead
if __name__ == "__main__":
    # Run the FastAPI application using uvicorn with auto-reload enabled
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
    #uvicorn src.app.main:app --reload
