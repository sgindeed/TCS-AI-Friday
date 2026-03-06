import os
import json
import httpx
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from prompt_templates import anomaly_prompt

load_dotenv()

MODEL = os.getenv("MODEL")
API_KEY = os.getenv("API_KEY")
API_ENDPOINT = os.getenv("API_ENDPOINT")

client = httpx.Client(verify=False)

llm = ChatOpenAI(
    base_url=API_ENDPOINT,
    model=MODEL,
    api_key=API_KEY,
    http_client=client
)


def clean_llm_json(text):
    """
    Removes markdown code blocks and extracts JSON safely
    """

    # remove ```json or ```
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    text = text.strip()

    # extract JSON object if extra text exists
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def explain_anomaly(data, anomalies):

    prompt = anomaly_prompt(data, anomalies)

    response = llm.invoke(prompt)

    content = response.content

    cleaned = clean_llm_json(content)

    try:
        parsed = json.loads(cleaned)

        return {
            "summary": parsed.get("summary", ""),
            "causes": parsed.get("causes", []),
            "usersAffected": parsed.get("usersAffected", ""),
            "riskLevel": parsed.get("riskLevel", ""),
            "steps": parsed.get("steps", [])
        }

    except Exception:

        # fallback if parsing fails
        return {
            "summary": cleaned,
            "causes": [],
            "usersAffected": "Unknown",
            "riskLevel": "Unknown",
            "steps": []
        }