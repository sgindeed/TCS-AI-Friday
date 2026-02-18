import os
import shutil
import gc
import whisper
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# Load environment variables
load_dotenv()

app = FastAPI()

# -----------------------------
# DeepSeek Client Setup
# -----------------------------
deepseek_client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
)

MODEL_NAME = os.getenv("MODEL_NAME")

# -----------------------------
# Load Whisper Model (CPU)
# -----------------------------
print("Loading Whisper model...")
whisper_model = whisper.load_model("small")
print("Whisper model loaded.")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Helper: Extract PDF Text
# -----------------------------
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text


# -----------------------------
# Helper: Transcribe Audio
# -----------------------------
def transcribe_audio(file_path):
    result = whisper_model.transcribe(
        file_path,
        fp16=False  # IMPORTANT for CPU
    )
    gc.collect()
    return result["text"]


# -----------------------------
# Helper: Analyze Text via DeepSeek
# -----------------------------
def analyze_text(transcript):

    prompt = f"""
    You are a professional Call Quality Analyst.

    Analyze the following transcript:

    {transcript}

    Return STRICT JSON:
    {{
        "summary": "...",
        "customer_sentiment": "Positive/Neutral/Negative",
        "sentiment_score": 1-10,
        "agent_performance_score": 1-10,
        "agent_feedback": "..."
    }}
    """

    response = deepseek_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You analyze call center conversations."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# -----------------------------
# Main Endpoint
# -----------------------------
@app.post("/analyze")
async def analyze(
    transcript: str = Form(None),
    file: UploadFile = File(None)
):

    extracted_text = None

    # 1️⃣ Text box
    if transcript:
        extracted_text = transcript

    # 2️⃣ File input
    elif file:

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_ext = file.filename.lower()

        # TXT
        if file_ext.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()

        # PDF
        elif file_ext.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_path)

        # AUDIO
        elif file_ext.endswith((".mp3", ".wav", ".mp4")):
            extracted_text = transcribe_audio(file_path)

        else:
            return {"error": "Unsupported file type."}

    else:
        return {"error": "Provide transcript text or file."}

    # 3️⃣ Send to DeepSeek
    analysis_result = analyze_text(extracted_text)

    return {
        "transcript": extracted_text,
        "analysis": analysis_result
    }


@app.get("/")
def health():
    return {"status": "AI service running"}
