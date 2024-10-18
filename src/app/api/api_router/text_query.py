from typing import List, Dict
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.domain.information_extraction.feature_extractor import clip
from src.domain.search_engine.vector_database import FaissDatabase
from src.common.query_processing import Text_Preprocessing
from langdetect import detect
from googletrans import Translator

import time

# Define the router
side_bars = APIRouter()

# Define a Pydantic model to represent the data structure
class TextQueryItem(BaseModel):
    id: int
    query: str

class SidebarData(BaseModel):
    model: str
    textQuery: Dict[int, TextQueryItem]  # Dictionary với key là id và value là TextQueryItem
    topK: str

# Function to compute harmonic distance
def harmonic(distance1: float, distance2: float, alpha: float = 1.0) -> float:
    """Tính toán khoảng cách harmonic."""
    return ((1 + alpha) * distance1 * distance2) / (alpha * distance1 + distance2)

# Function to filter and find consecutive frames
def filter_and_find_consecutive(query_result1: List[Dict], query_result2: List[Dict], threshold: int = 50):
    """Lọc các video_id chung và tìm frame liên tiếp giữa query1 và query2."""
    filtered_results = []
    
    # Duyệt qua từng kết quả của query 1 và query 2
    for res1 in query_result1:
        for res2 in query_result2:
            if res1['video_id'] == res2['video_id']:  # Kiểm tra nếu video_id giống nhau
                frame_diff = int(res2['frame_id']) - int(res1['frame_id'])
                
                # Kiểm tra nếu frame liên tiếp theo điều kiện (0 < frame_diff < threshold)
                if 0 < frame_diff < threshold:
                    # Nếu frame liên tiếp, thêm vào danh sách kết quả
                    filtered_results.append([res1, res2])
    
    return filtered_results

# Function to process queries, compute harmonic and return results
def process_queries(query1_result: List[Dict], query2_result: List[Dict] = None, alpha: float = 1.0, threshold: int = 50):
    """Xử lý các truy vấn, tìm frame liên tiếp và trả về kết quả dưới dạng list[dict]."""
    
    # Nếu chỉ có 1 query, thì chỉ trả về danh sách kết quả từ query đó
    if query2_result is None:
        # Trả về kết quả query 1
        return [{'video_id': res1['video_id'], 'frame_id': res1['frame_id'], 'position': res1['position']} for res1 in query1_result]

    # Nếu có cả query 1 và query 2, tìm các frame liên tiếp
    consecutive_frames = filter_and_find_consecutive(query1_result, query2_result, threshold)
    print("consecutive_frames:", consecutive_frames)
    
    # Tính harmonic cho mỗi cặp frame liên tiếp và lưu lại kết quả với cả res1 và res2
    results_with_harmonic = []
    for res1, res2 in consecutive_frames:
        try:
            harmonic_value = harmonic(float(res1.get('distance', 1)), float(res2.get('distance', 1)), alpha)
        except (KeyError, ValueError) as e:
            print(f"Error calculating harmonic value: {e}")
            continue

        print("harmonic_value:", harmonic_value)
        print("res1:", res1, "res2:", res2)
        
        # Lưu lại kết quả với cả res1 và res2 (chỉ lấy các khóa 'video_id', 'frame_id', 'position')
        results_with_harmonic.append({
            'video_id': res1['video_id'],
            'frame_id': res1['frame_id'],
            'position': res1['position']
        })
        results_with_harmonic.append({
            'video_id': res2['video_id'],
            'frame_id': res2['frame_id'],
            'position': res2['position']
        })

    # Trả về danh sách các phần tử dưới dạng list[dict]
    return results_with_harmonic

# Initialize the components
faiss = FaissDatabase()
faiss.load_index('clip', r'src/app/static/data/faiss/clip.index')

# Initialize translation and text preprocessing
translator = Translator()  # Google Translate
text_preprocessor = Text_Preprocessing()

# Function to remove 'distances' field from each result
def remove_distances(result: List[Dict]) -> List[Dict]:
    """Remove 'distances' field from each dictionary in the result list."""
    cleaned_result = []
    for item in result:
        if isinstance(item, dict):
            cleaned_item = {k: v for k, v in item.items() if k != 'distance'}
            cleaned_result.append(cleaned_item)
        else:
            print("Item is not a dict:", item)
    return cleaned_result

# Main API route to handle the sidebar data
@side_bars.post('/')
def handle_sidebar_data(data: SidebarData):
    print(f"Model: {data.model}")
    print(f"topK: {data.topK}")

    start = time.time()

    # Process each query in textQuery dict
    translated_queries = {}
    for item in data.textQuery.values():
        print(f"Processing Query ID {item.id}: {item.query}")

        # Detect the language of the text
        detected_lang = detect(item.query)
        print(f"Detected language for Query ID {item.id}: {detected_lang}")

        # Translate if the detected language is Vietnamese
        if detected_lang == 'vi':
            print(f"Translating Query ID {item.id} from Vietnamese to English...")
            translated_text = translator.translate(str(item.query), src="vi", dest="en").text
            print(f"Translated text for Query ID {item.id}: {translated_text}")
        else:
            # If not Vietnamese, use the original text
            translated_text = item.query

        # Preprocess the text
        preprocessed_text = text_preprocessor(translated_text)
        translated_queries[item.id] = preprocessed_text

    # Xử lý truy vấn dựa trên model
    if data.model == 'Clip':
        result = []
        query1_result = []
        query2_result = []

        # Process each query and calculate distances
        for query_id, processed_query in translated_queries.items():
            vector = clip.embed_query(processed_query)
            query_result = faiss.search('clip', vector, int(data.topK))

            # Thêm kiểm tra in ra kết quả
            print(f"Query Result for query {query_id}: {query_result}")

            # Kiểm tra cấu trúc của query_result
            if not isinstance(query_result, list):
                print(f"Error: query_result for query_id {query_id} is not a list. It is {type(query_result)}")
                continue

            # Kiểm tra xem các phần tử trong query_result có phải là dict hay không
            if not all(isinstance(item, dict) for item in query_result):
                print(f"Error: Not all items in query_result for query_id {query_id} are dicts.")
                for item in query_result:
                    print(f"Item: {item} (Type: {type(item)})")
                continue

            # Kiểm tra và phân loại kết quả theo từng query
            if len(query_result) > 0:
                print(f"query_result[{query_id}] is a list of {len(query_result)} items")
                if query_id == 0:
                    query1_result = query_result  # Assign the whole list
                elif query_id == 1:
                    query2_result = query_result
            else:
                print(f"Error: query_result for query_id {query_id} is empty.")

        # Nếu chỉ có kết quả cho query 1, trả về query 1
        if query1_result and not query2_result:
            result = process_queries(query1_result)

        # Nếu có cả kết quả cho query 1 và query 2, thực hiện tính toán
        elif query1_result and query2_result:
            combined_result = process_queries(query1_result, query2_result, alpha=1.0, threshold=500)
            result = combined_result  # Kết quả trả về sẽ chứa cả res1 và res2
        else:
            result = {"error": "Not enough query results."}

    else:
        result = {"error": "Invalid model"}

    queryTime = time.time()
    print("day la kq", result)
    print('Total Processing Time:', queryTime - start)
    return JSONResponse(content={"data": result})
