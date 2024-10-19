from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
from src.app.api.api_router.text_query import faiss
from src.domain.information_extraction.feature_extractor import clip  
import shutil
import os

# Tạo router cho các endpoint liên quan tới date
router = APIRouter()

# Chỉ định một đường dẫn để lưu file upload
UPLOAD_DIR = "src/uploads/"  # Đảm bảo thư mục này tồn tại
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post('/image')
async def image_query(file: UploadFile = File(...), model: str = Form(...)):
    print(file, model)
    # Kiểm tra điều kiện và raise error nếu cần
    if not file:
        raise HTTPException(status_code=400, detail="No Images or File Uploaded")
    
    try:
        # Lưu file upload vào server
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        print(file_location)

        # Đọc dữ liệu từ file và lưu vào buffer
        with open(file_location, "wb") as buffer:
            contents = await file.read()  # Await để đọc file
            buffer.write(contents)  # Ghi dữ liệu vào file

        # Sử dụng hàm embed_images với file đã upload
        vector_query = clip.embed_images([file_location])  # Đảm bảo rằng hàm này nhận danh sách file
        
        if model == "Clip":
            result = faiss.search('clip', vector_query[0], k=300)  # Chỉ tìm kiếm cho query đầu tiên
            # Loại bỏ trường distance
            results = [
                {key: value for key, value in item.items() if key != 'distance'} 
                for item in result
            ]
        else:
            raise HTTPException(status_code=404, detail="Model not supported")
    
    except Exception as e:
        # Log lỗi trong quá trình xử lý
        print(f"Error occurred: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal error occurred")
    
    # Trả về kết quả
    return JSONResponse(content={"data": results})