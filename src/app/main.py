from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import os
from src.app.api.api_router.date_filter import router as date_router
from src.app.api.api_router.text_query import side_bars
from src.app.api.api_router.search import search_api
from src.app.api.api_router.color_search import router as color_router
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
app.include_router(side_bars, prefix="/side-bar")

# Include the router for search routes
app.include_router(search_api, prefix="/search")

app.include_router(date_router)
# Include the router for image routes
app.include_router(side_bars, prefix="/side-bar")

# Include the router for search routes
app.include_router(search_api, prefix="/search")
app.include_router(color_router)
if __name__ == "__main__":
    # Run the FastAPI application using uvicorn with auto-reload enabled
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
