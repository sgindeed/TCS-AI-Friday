import os
import json
import time
import re
import httpx

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv


# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

if not API_KEY or not BASE_URL or not MODEL_NAME:
    raise ValueError("Missing API_KEY, BASE_URL, or MODEL_NAME in .env")


# -----------------------------
# FASTAPI INIT
# -----------------------------

app = FastAPI(title="Enterprise Banking AI Engine")


# For hackathon demo only (avoid in production)
http_client = httpx.Client(verify=False)

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0,
    api_key=API_KEY,
    base_url=BASE_URL,
    http_client=http_client
)


class QueryRequest(BaseModel):
    customer_query: str


# -----------------------------
# HELPERS
# -----------------------------

def clean_output(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"```json|```", "", text)
    return text.strip()


def extract_json(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return {}
        return {}


# -----------------------------
# MAIN ENDPOINT
# -----------------------------

@app.post("/analyze")
def analyze_query(request: QueryRequest):

    start_time = time.time()

    prompt = f"""
You are an Enterprise Banking Complaint Analysis AI.

Analyze the customer complaint and return structured JSON.

Objectives:
1. Classify the complaint
2. Detect fraud or financial risk
3. Assign priority level
4. Determine escalation requirement
5. Assign responsible department
6. Generate risk score (0-100)
7. Detect sentiment
8. Provide clear banking resolution steps
9. Create internal ticket details
10. Draft professional banking agent response

Strict Business Rules:
- If account emptied, unauthorized transaction, scam, phishing, or money loss → classify as Fraud
- Fraud cases must be Critical priority
- Fraud cases require escalation
- Financial risk must influence risk score
- Use only banking terminology
- Avoid medical or unrelated wording

make sure you dont type the customer name in the output and the agent_reply should start with "Dear Customer..."
Return STRICT RAW JSON only in this structure:

{{
  "classification": {{
    "primary_category": "",
    "sub_category": ""
  }},
  "summary": {{
    "main_issue": ""
  }},
  "priority": {{
    "level": ""
  }},
  "fraud_risk": {{
    "risk_score": 0,
    "risk_level": ""
  }},
  "sentiment": {{
    "sentiment_label": ""
  }},
  "escalation": {{
    "required": false,
    "department": ""
  }},
  "suggested_resolution_steps": [],
  "auto_ticket": {{
    "ticket_title": "",
    "department": "",
    "SLA_hours": 0
  }},
  "agent_reply_draft": ""
}}

Customer Complaint:
{request.customer_query}
"""

    messages = [
        SystemMessage(
            content=(
                "You are a banking AI engine. "
                "Return strict raw JSON only. "
                "No markdown. No explanations. "
                "Banking domain only."
            )
        ),
        HumanMessage(content=prompt)
    ]

    try:
        response = llm.invoke(messages)
        raw_output = response.content
    except Exception as e:
        return {"error": str(e)}

    cleaned = clean_output(raw_output)
    parsed = extract_json(cleaned)

    if not parsed:
        return {
            "error": "Model did not return valid JSON",
            "raw_response": raw_output
        }

    result = {
        "complaint_type": parsed.get("classification", {}).get("primary_category"),
        "sub_category": parsed.get("classification", {}).get("sub_category"),
        "summary": parsed.get("summary", {}).get("main_issue"),
        "priority": parsed.get("priority", {}).get("level"),
        "risk_score": parsed.get("fraud_risk", {}).get("risk_score"),
        "risk_level": parsed.get("fraud_risk", {}).get("risk_level"),
        "sentiment": parsed.get("sentiment", {}).get("sentiment_label"),
        "escalation_required": parsed.get("escalation", {}).get("required"),
        "handled_by": parsed.get("escalation", {}).get("department"),
        "resolution_steps": parsed.get("suggested_resolution_steps", []),
        "ticket_title": parsed.get("auto_ticket", {}).get("ticket_title"),
        "ticket_department": parsed.get("auto_ticket", {}).get("department"),
        "SLA_hours": parsed.get("auto_ticket", {}).get("SLA_hours"),
        "agent_reply": parsed.get("agent_reply_draft"),
        "metrics": {
            "input_word_count": len(request.customer_query.split()),
            "response_time_seconds": round(time.time() - start_time, 2)
        }
    }

    return result


@app.get("/health")
def health():
    return {"status": "Banking AI Engine Running"}