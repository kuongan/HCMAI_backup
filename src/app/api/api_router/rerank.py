from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
from src.app.api.api_router.date_filter import convert_urls
from src.app.api.api_router.text_query import faiss
from src.domain.information_extraction.feature_extractor import clip  


# Tạo router cho các endpoint liên quan tới date
router = APIRouter()
class URLs(BaseModel):
    urls: list[str]  # This expects 'urls', not 'images'
    model: str

def remove_http_prefix(urls):
    # Phần cần loại bỏ
    http_prefix = r"http://127.0.0.1:8000/"
    
    # Phần thay thế
    replacement = r"src/app/"

    clean_urls = [url.replace(http_prefix, replacement) for url in urls]

    return clean_urls

@router.post('/rerank')
async def filter_by_date(data: URLs):

    # Kiểm tra điều kiện và raise error nếu cần
    if not data.urls:
        raise HTTPException(status_code=400, detail="No Reranked Images")
    try:
        urls = remove_http_prefix(data.urls)     
        vector_queries = clip.embed_images(urls)
        if data.model == "Clip": 
            results = []
            for query in vector_queries: 
                result = faiss.search('clip', query, k=300)
                results.append(result) 
            # Gộp các list con thành một list duy nhất
            combined_result = [item for sublist in results for item in sublist]
            # Sắp xếp các phần tử dựa trên thuộc tính distance theo thứ tự giảm dần và lấy top 

            sorted_result = sorted(combined_result, key=lambda x: x['distance'], reverse=True)[:300]
            # Loại bỏ trường distance
            sorted_result = [
                {key: value for key, value in item.items() if key != 'distance'} 
                for item in sorted_result
            ]

        else:
            raise HTTPException(status_code=404, detail="Model not supported")
    
    except Exception as e:
        # Log lỗi trong quá trình xử lý
        print(f"Error occurred: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal error occurred")
    
    # Trả về kết quả
    return JSONResponse(content={"data": sorted_result})


