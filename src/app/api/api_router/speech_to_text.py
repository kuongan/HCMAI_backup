from fastapi import FastAPI, File, UploadFile, APIRouter
import os
import wave
import scipy.io.wavfile as wavfile
from fastapi.responses import JSONResponse

# Load model directly
from transformers import pipeline
transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small", device="cuda")
router = APIRouter()

# Tạo thư mục lưu trữ nếu chưa có
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
        
@router.post("/speech_to_text")
async def speech_to_text(audioFile: UploadFile = File(...)):
    # Lưu file vào thư mục tạm thời
    file_location = os.path.join(UPLOAD_FOLDER, audioFile.filename)
    with open(file_location, "wb") as file:
        file.write(await audioFile.read())

    # Xử lý file .wav
    try:
        text = transcriber(file_location)['text']
        return JSONResponse(content={"transcription": text}, status_code=200)        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)