from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
from src.domain.search_engine.Elastic_search.elastic_search import es
import os
router = APIRouter()

# Path to your hierarchical JSON data
json_file_path = os.path.join('src','app','static','data', 'bbox_labels_600_hierarchy_with_names.json')

# Pydantic model for incoming search payload
class ObjectSearchPayload(BaseModel):
    objectClass: str
    min: int
    max: int

# Load the JSON data function
def load_data():
    try:
        with open(json_file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

# Find subcategories based on the category chain
def find_subcategories(category, chain):
    if not chain:
        return category.get("Subcategory", [])
    
    for subcat in category.get("Subcategory", []):
        if subcat["DisplayName"].lower() == chain[0].lower():
            if len(chain) > 1:
                return find_subcategories(subcat, chain[1:])
            else:
                return subcat.get("Subcategory", [])
    return []

# Search through the entire hierarchy for a matching class (when the user types directly)
def search_classes(category, query, result_list, path=""):
    if query.lower() in category["DisplayName"].lower():
        result_list.append({
            "DisplayName": category["DisplayName"],
            "path": path.strip(" > ")
        })
    
    if "Subcategory" in category:
        for subcat in category["Subcategory"]:
            search_classes(subcat, query, result_list, path + " > " + category["DisplayName"])

# Endpoint to suggest based on query and chain
@router.get("/suggest")
async def suggest(query: str = "", chain: str = ""):
    data = load_data()
    
    chain_list = [c.strip() for c in chain.split(">") if c.strip()]
    if chain_list:
        subcategories = find_subcategories(data, chain_list)
        return JSONResponse(content=[{"DisplayName": subcat["DisplayName"], "path": chain} for subcat in subcategories])

    result_list = []
    for category in data.get("Subcategory", []):
        search_classes(category, query, result_list)
    
    return JSONResponse(content=result_list)

# Elasticsearch-based search endpoint for handling object class, min, and max
@router.post("/object/")
async def objectsearch(payload: ObjectSearchPayload):
    objectclass = payload.objectClass
    min_count = payload.min
    max_count = payload.max
    # Check if the Elasticsearch client is connected
    if es.client:
        # Perform the search with the Elasticsearch query
        search_results = es.search_od(
            index_name='od_index',
            query=objectclass,
            min_count=min_count,
            max_count=max_count,
            topk=100,
        )
        return JSONResponse(content={'data': search_results})
    else:
        return JSONResponse(content={'error': 'Elasticsearch not connected'}, status_code=500)
