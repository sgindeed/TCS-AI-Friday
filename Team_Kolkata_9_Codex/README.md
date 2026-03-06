# AI Anomaly Explanation Assistant

### DevOps Log Analysis using FastAPI, LLMs, and a Web Dashboard

## 1. Project Overview

The **AI Anomaly Explanation Assistant** is a DevOps support tool designed to automatically detect anomalies in infrastructure logs and telemetry data, and generate human-readable explanations along with remediation suggestions.

The system combines:

* **Rule-based anomaly detection**
* **LLM-powered incident explanation**
* **FastAPI backend**
* **Interactive web dashboard**

The tool helps DevOps teams quickly understand system failures, investigate root causes, and take corrective action.

---

# 2. System Architecture

The system follows a **client–server architecture**.

```
User
 │
 ▼
Frontend Web UI (HTML + Tailwind + JavaScript)
 │
 │ HTTP POST /analyze
 ▼
FastAPI Backend
 │
 ├── Input Parser
 ├── Anomaly Detector
 └── LLM Explanation Engine
 │
 ▼
Response JSON
 │
 ▼
Frontend Dashboard Rendering
```

---

# 3. Key Features

### 1. Automatic Anomaly Detection

The system identifies irregularities in infrastructure metrics such as:

* Processed records
* Transaction counts
* System performance metrics

Example anomaly:

```
Expected: 10000
Actual: 1200
Deviation: 88%
```

---

### 2. AI-Powered Root Cause Analysis

Once anomalies are detected, an LLM analyzes logs and generates:

* Incident summary
* Possible root causes
* Impact assessment
* Investigation steps

---

### 3. Multiple Input Formats Supported

The system accepts:

#### Structured JSON

```json
{
  "pipeline": "orders_etl",
  "metric": "orders_processed",
  "expected": 10000,
  "actual": 1200,
  "logs": [
    "INFO Starting ETL job",
    "ERROR API timeout"
  ]
}
```

#### Plain Text Logs

```
pipeline orders_etl failed due to API timeout
```

The backend automatically converts text into structured telemetry.

---

### 4. Interactive Dashboard

The UI displays:

* Detected anomalies
* Incident summary
* Root causes
* Impact assessment
* Suggested investigation steps

---

# 4. Technology Stack

## Frontend

| Technology     | Purpose           |
| -------------- | ----------------- |
| HTML           | UI structure      |
| TailwindCSS    | Styling           |
| JavaScript     | API communication |
| Material Icons | Dashboard visuals |

---

## Backend

| Technology | Purpose                |
| ---------- | ---------------------- |
| FastAPI    | REST API server        |
| Pydantic   | Data validation        |
| Python     | Backend logic          |
| LLM API    | Explanation generation |

---

# 5. Folder Structure

```
project-root
│
├── backend
│   ├── app.py
│   ├── anomaly_detector.py
│   ├── llm_explainer.py
│   ├── text_parser.py
│   └── requirements.txt
│
├── frontend
│   └── index.html
│
└── README.md
```

---

# 6. Backend Components

## 6.1 FastAPI Application (`app.py`)

This is the main API server responsible for:

* receiving user input
* parsing telemetry data
* detecting anomalies
* generating explanations

### Endpoint

```
POST /analyze
```

Request body:

```
{
  "input": "pipeline orders_etl failed due to API timeout"
}
```

or

```
{
 "pipeline": "orders_etl",
 "metric": "orders_processed",
 "expected": 10000,
 "actual": 1200,
 "logs": []
}
```

---

## 6.2 Anomaly Detection (`anomaly_detector.py`)

The anomaly detection module performs rule-based analysis.

Example logic:

```
deviation = abs(expected - actual) / expected
```

If deviation exceeds a defined threshold (e.g. 30%), the system flags an anomaly.

Example anomalies:

* Large deviation in processed records
* Error logs detected
* Missing data

---

## 6.3 Text Parser (`text_parser.py`)

Converts plain text logs into structured JSON.

Example:

Input:

```
pipeline orders_etl failed due to timeout
```

Output:

```
{
 "pipeline":"orders_etl",
 "metric":"unknown_metric",
 "expected":0,
 "actual":0,
 "logs":["pipeline orders_etl failed due to timeout"]
}
```

---

## 6.4 LLM Explanation Engine (`llm_explainer.py`)

This module sends anomaly information to an LLM to generate human-readable explanations.

The LLM generates:

* incident summary
* possible causes
* user impact
* remediation steps

Example response:

```
{
 "summary": "...",
 "causes": [],
 "usersAffected": "...",
 "riskLevel": "...",
 "steps": []
}
```

---

# 7. Frontend Dashboard

The frontend is implemented as a **single HTML page with JavaScript**.

Main components:

### JSON Input Panel

Allows users to paste:

* infrastructure logs
* telemetry JSON
* plain text errors

---

### AI Analysis Report Panel

Displays:

* detected anomalies
* incident summary
* possible causes
* impact assessment
* suggested investigation steps

---

# 8. Frontend–Backend Communication

The frontend communicates with the backend using the **Fetch API**.

Example request:

```javascript
fetch("http://localhost:8000/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(payload)
})
```

The backend returns structured JSON which is rendered dynamically in the dashboard.

---

# 9. Example Workflow

### Step 1 — User Input

User pastes logs:

```
pipeline orders_etl failed due to API timeout
```

---

### Step 2 — Frontend Request

```
POST /analyze
```

```
{
 "input":"pipeline orders_etl failed due to API timeout"
}
```

---

### Step 3 — Backend Processing

1. Parse input
2. Detect anomalies
3. Generate AI explanation

---

### Step 4 — Response

```
{
 "detected_anomalies":[
   "Error logs detected"
 ],
 "summary":"Orders ETL pipeline failed due to supplier API timeout",
 "causes":[
   "Supplier API rate limit exceeded"
 ],
 "usersAffected":"Customers and inventory teams",
 "riskLevel":"High",
 "steps":[
   "Retry job with exponential backoff",
   "Increase API timeout configuration"
 ]
}
```

---

### Step 5 — Dashboard Rendering

The frontend updates the report UI.

---

# 10. Running the Project

## Start Backend

```
uvicorn app:app --reload --port 8000
```

---

## Run Frontend

Use a simple static server:

```
python -m http.server 3000
```

Open:

```
http://localhost:3000
```

---

# 11. Future Improvements

Possible enhancements include:

* real-time log ingestion
* anomaly detection using ML models
* historical incident database
* alerting integrations (Slack, PagerDuty)
* observability dashboards

---

# 12. Conclusion

The AI Anomaly Explanation Assistant demonstrates how **rule-based anomaly detection combined with LLM reasoning** can significantly improve incident investigation workflows.

By automating anomaly detection and explanation generation, the system enables DevOps teams to reduce troubleshooting time and improve system reliability.