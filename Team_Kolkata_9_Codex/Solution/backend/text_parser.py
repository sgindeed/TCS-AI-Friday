import re

def parse_text_to_json(text):

    pipeline = re.search(r'pipeline[:\- ]+(.*)', text, re.I)
    metric = re.search(r'metric[:\- ]+(.*)', text, re.I)
    expected = re.search(r'expected[:\- ]+(\d+)', text, re.I)
    actual = re.search(r'actual[:\- ]+(\d+)', text, re.I)

    logs = re.findall(r'(INFO|ERROR|WARNING).*', text)

    return {
        "pipeline": pipeline.group(1) if pipeline else "unknown",
        "metric": metric.group(1) if metric else "unknown",
        "expected": int(expected.group(1)) if expected else 0,
        "actual": int(actual.group(1)) if actual else 0,
        "logs": logs
    }