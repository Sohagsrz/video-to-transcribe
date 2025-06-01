import os
import shutil
import uuid
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
import ffmpeg
import whisper
from typing import Optional

ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov'}
TEMP_DIR = 'temp'

os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = whisper.load_model("base")


def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_files(*filepaths):
    for path in filepaths:
        if path and os.path.exists(path):
            os.remove(path)

@app.get("/", response_class=HTMLResponse)
def index(request: Request, error: Optional[str] = None, transcript: Optional[str] = None, transcript_file: Optional[str] = None):
    return templates.TemplateResponse("index.html", {"request": request, "error": error, "transcript": transcript, "transcript_file": transcript_file})

@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    if not file.filename or not allowed_file(file.filename):
        return templates.TemplateResponse("index.html", {"request": request, "error": "Please upload a valid video file (.mp4, .avi, .mov)."})
    # Save uploaded file
    file_id = str(uuid.uuid4())
    video_path = os.path.join(TEMP_DIR, f"{file_id}_{file.filename}")
    with open(video_path, "wb") as f:
        f.write(await file.read())
    # Extract audio
    audio_path = os.path.join(TEMP_DIR, f"{file_id}.wav")
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
    except Exception as e:
        cleanup_files(video_path, audio_path)
        return templates.TemplateResponse("index.html", {"request": request, "error": f"Audio extraction failed: {e}"})
    # Transcribe
    try:
        result = model.transcribe(audio_path)
        transcript = result["text"].strip()
    except Exception as e:
        cleanup_files(video_path, audio_path)
        return templates.TemplateResponse("index.html", {"request": request, "error": f"Transcription failed: {e}"})
    # Save transcript
    transcript_file = os.path.join(TEMP_DIR, f"{file_id}.txt")
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)
    # Clean up video and audio after rendering
    task = BackgroundTask(cleanup_files, video_path, audio_path)
    return templates.TemplateResponse("index.html", {"request": request, "transcript": transcript, "transcript_file": os.path.basename(transcript_file)}, background=task)

@app.get("/download/{filename}")
def download_transcript(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        return HTMLResponse("File not found", status_code=404)
    # Clean up after sending
    task = BackgroundTask(cleanup_files, file_path)
    return FileResponse(file_path, media_type='text/plain', filename=filename, background=task) 