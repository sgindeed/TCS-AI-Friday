from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anomaly_detector import detect_anomaly
from llm_explainer import explain_anomaly
from text_parser import parse_text_to_json
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserInput(BaseModel):
    input: str


@app.post("/analyze")
async def analyze(data: UserInput):

    raw_input = data.input.strip()

    data_dict = None

    # ---------------------------
    # Try parsing input as JSON
    # ---------------------------
    try:
        parsed = json.loads(raw_input)

        # If JSON is already a dictionary
        if isinstance(parsed, dict):
            data_dict = parsed

        # If JSON is a string containing JSON
        elif isinstance(parsed, str):
            parsed_again = json.loads(parsed)
            if isinstance(parsed_again, dict):
                data_dict = parsed_again

    except Exception:
        pass

    # ---------------------------
    # If not JSON → treat as text
    # ---------------------------
    if data_dict is None:
        data_dict = parse_text_to_json(raw_input)

    # ---------------------------
    # Ensure required fields exist
    # ---------------------------
    data_dict.setdefault("pipeline", "unknown_pipeline")
    data_dict.setdefault("metric", "unknown_metric")
    data_dict.setdefault("expected", 0)
    data_dict.setdefault("actual", 0)
    data_dict.setdefault("logs", [])

    # ---------------------------
    # Detect anomalies
    # ---------------------------
    anomalies = detect_anomaly(data_dict)

    # ---------------------------
    # Generate explanation
    # ---------------------------
    if anomalies:
        explanation = explain_anomaly(data_dict, anomalies)
    else:
        explanation = {
            "summary": "No anomaly detected",
            "causes": [],
            "usersAffected": "None",
            "riskLevel": "Low",
            "steps": []
        }

    return {
        "detected_anomalies": anomalies,
        **explanation
    }