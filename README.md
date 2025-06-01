# FastAPI Video Transcription App

A web app to upload video files, extract audio, transcribe speech to text using OpenAI Whisper, and download the transcript.

## Features

- Upload video files (`.mp4`, `.avi`, `.mov`)
- Extracts audio using ffmpeg
- Transcribes audio to text using OpenAI Whisper
- Displays transcript on the web page
- Download transcript as `.txt`
- Cleans up temporary files automatically
- Error handling for invalid files and processing issues
- Simple Bootstrap UI

## Project Structure

```
transcribe/
├── temp/                # Temporary files (audio, transcripts)
├── templates/           # Jinja2 HTML templates
│   └── index.html
├── .gitignore           # Git ignore file
├── main.py              # Main FastAPI application
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
```

## Tech Stack

- FastAPI (backend)
- Jinja2 (templating)
- ffmpeg-python (audio extraction)
- OpenAI Whisper (speech-to-text)
- Bootstrap (UI)

## Requirements

- Python 3.8+
- ffmpeg (must be installed and in your PATH)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Install Python dependencies
pip install -r requirements.txt
```

## Whisper Installation Note

If you encounter issues with the `whisper` package, ensure you have the correct version:

```bash
pip uninstall whisper -y
pip install git+https://github.com/openai/whisper.git
```

## Running the App

```bash
uvicorn main:app --reload
```

Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

1. Upload a video file using the form.
2. Wait for processing (may take time for large files).
3. View the transcript on the page.
4. Download the transcript as a `.txt` file.

## Deployment

- Do **not** upload sensitive videos to a public server.
- For production, use a production ASGI server and secure file handling.

## .gitignore

A `.gitignore` is provided to avoid committing temp files and other unnecessary files.

## License

MIT
