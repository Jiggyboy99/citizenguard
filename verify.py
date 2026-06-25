"""
CitizenGuard - core verification engine (Week 1 MVP, steps 3-4)

What this does:
  1. Pulls REAL recent air-quality readings near a location from OpenAQ v3.
  2. Feeds those readings + a citizen's report into an LLM.
  3. Returns a verdict (verified / unverified / unclear) WITH a citation.

This is the whole product in one file. The Guardian security layer and the
Gradio UI come later - this is the spine they bolt onto.

Run it:
    pip install -r requirements.txt
    cp .env.example .env        # then paste your two keys into .env
    python verify.py
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# --- Config -----------------------------------------------------------------
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq model names change over time - confirm the current one in your Groq
# console (console.groq.com) if this errors out.
GROQ_MODEL = "llama-3.3-70b-versatile"

OPENAQ_BASE = "https://api.openaq.org/v3"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Default search point. Lat/lon of Lagos, NG - change to wherever you want to
# study. Note: OpenAQ sensor coverage varies a lot by city. If you get no data,
# try a city with dense coverage, e.g. Delhi (28.6139, 77.2090) or
# Los Angeles (34.0522, -118.2437).
DEFAULT_LAT = 6.5244
DEFAULT_LON = 3.3792
SEARCH_RADIUS_M = 25000  # OpenAQ max radius is 25000 m


# --- Step 3: fetch real data ------------------------------------------------
def fetch_air_quality(lat=DEFAULT_LAT, lon=DEFAULT_LON, radius=SEARCH_RADIUS_M):
    """Return a list of recent readings near (lat, lon) from OpenAQ v3.

    Each reading: {"parameter", "value", "unit", "datetime", "location"}.
    Returns [] if nothing is found (handle that gracefully upstream).
    """
    if not OPENAQ_API_KEY:
        raise RuntimeError("OPENAQ_API_KEY is missing - put it in your .env file.")

    headers = {"X-API-Key": OPENAQ_API_KEY}

    # 1) find nearby monitoring locations
    loc_resp = requests.get(
        f"{OPENAQ_BASE}/locations",
        headers=headers,
        params={"coordinates": f"{lat},{lon}", "radius": radius, "limit": 5},
        timeout=30,
    )
    loc_resp.raise_for_status()
    locations = loc_resp.json().get("results", [])
    if not locations:
        return []

    readings = []
    for loc in locations:
        loc_id = loc.get("id")
        loc_name = loc.get("name", "unknown")

        # map this location's sensor ids -> parameter name + unit
        sensor_map = {}
        for s in loc.get("sensors", []):
            param = s.get("parameter", {})
            sensor_map[s.get("id")] = (
                param.get("name", "?"),
                param.get("units", ""),
            )

        # 2) get the latest measurement from each sensor at this location
        latest_resp = requests.get(
            f"{OPENAQ_BASE}/locations/{loc_id}/latest",
            headers=headers,
            timeout=30,
        )
        if latest_resp.status_code != 200:
            continue

        for m in latest_resp.json().get("results", []):
            name, unit = sensor_map.get(m.get("sensorsId"), ("?", ""))
            readings.append(
                {
                    "parameter": name,
                    "value": m.get("value"),
                    "unit": unit,
                    "datetime": (m.get("datetime") or {}).get("utc", "?"),
                    "location": loc_name,
                }
            )

    return readings


def format_readings(readings):
    """Turn the readings list into a compact string for the prompt."""
    if not readings:
        return "(no sensor data available for this location)"
    lines = []
    for r in readings:
        lines.append(
            f"- {r['parameter']} = {r['value']} {r['unit']} "
            f"at {r['datetime']} ({r['location']})"
        )
    return "\n".join(lines)


# --- Step 4: verify the report ----------------------------------------------
def load_prompt(path="prompts/verify_v1.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def verify_report(report_text, readings):
    """Ask the LLM to judge the report against the real readings.

    Returns a dict: {"verdict", "reasoning", "citation"}.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing - put it in your .env file.")

    template = load_prompt()
    prompt = template.replace("{real_data}", format_readings(readings)).replace(
        "{citizen_report}", report_text
    )

    resp = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    # the model should return pure JSON; strip fences just in case
    cleaned = content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "verdict": "unclear",
            "reasoning": "model did not return valid JSON",
            "citation": "none",
            "_raw": content,
        }


# --- Demo -------------------------------------------------------------------
if __name__ == "__main__":
    sample_report = (
        "Air near Sagamu Road in Ikorodu is moderately polluted right now"
    )

    print("Fetching real air-quality data...")
    data = fetch_air_quality()
    print(f"Got {len(data)} readings.\n")
    print(format_readings(data))
    print("\nVerifying the citizen report...\n")

    result = verify_report(sample_report, data)
    print(json.dumps(result, indent=2))
