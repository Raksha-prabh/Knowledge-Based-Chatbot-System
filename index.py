import os
import json
import requests
from flask import Flask, jsonify, render_template, request
import google.generativeai as genai
from knowledge_base import KnowledgeBase


app = Flask(__name__)
kb = KnowledgeBase()

# 1. SETUP THE FREE GOOGLE API CLIENT
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in your .env file!")

genai.configure(api_key=api_key)


# =====================================================================
# CHATBOT TOOLBELT (Your Custom Python Backend APIs)
# =====================================================================

def get_lat_long(city_name: str):
    """Internal helper to convert city strings to geolocation coordinates."""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        res = requests.get(url).json()
        if "results" in res and len(res["results"]) > 0:
            loc = res["results"][0]
            return loc["latitude"], loc["longitude"], loc.get("name", city_name)
    except Exception:
        pass
    return None, None, city_name


def get_live_weather(city: str) -> str:
    """Get the current live real-time weather and temperature data for a specific location or city name."""
    lat, lon, real_name = get_lat_long(city)
    if not lat:
        return f"Could not find coordinates for location: {city}"
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url).json()
        current = data.get("current_weather", {})
        if current:
            return f"Current weather in {real_name}: {current.get('temperature')}°C, Wind: {current.get('windspeed')} km/h."
    except Exception as e:
        return f"Error retrieving weather details: {str(e)}"
    return "Weather server down."


def search_tv_show(show_name: str) -> str:
    """Search for a TV show's profile including summary descriptions, genres, and database live rating score."""
    try:
        url = f"http://api.tvmaze.com/singlesearch/shows?q={show_name}"
        data = requests.get(url).json()
        if data:
            summary = data.get("summary", "").replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "")
            return (
                f"Official Title: {data.get('name')} | "
                f"Rating: {data.get('rating', {}).get('average', 'N/A')}/10 | "
                f"Genres: {', '.join(data.get('genres', []))} | "
                f"Plot Summary: {summary}"
            )
    except Exception:
        pass
    return f"Could not find any TV show logs matching '{show_name}'."


def get_public_holidays(country_code: str) -> str:
    """Get the official national bank/public holidays for a specific country abbreviation code (e.g., US, IN, GB)."""
    try:
        url = f"https://date.nager.at/api/v3/PublicHolidays/2026/{country_code.upper()}"
        res = requests.get(url).json()
        if isinstance(res, list) and len(res) > 0:
            holidays = [f"{h['date']}: {h['localName']}" for h in res[:5]]
            return f"Upcoming national holidays for {country_code.upper()}: " + ", ".join(holidays)
    except Exception:
        pass
    return f"Could not fetch upcoming holiday schedules for country code: {country_code}."


# 2. BIND THE REMAINING PYTHON FUNCTIONS DIRECTLY TO THE FREE GEMINI ENGINE
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=[get_live_weather, search_tv_show, get_public_holidays]
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please send a valid message."}), 400

    try:
        # Check local knowledge base first to optimize speeds and prevent rate limits
        learned_match = kb.get_learned_response(user_message)
        if learned_match:
            reply = learned_match["response"]
            kb.add_conversation(user_message, reply)
            return jsonify({"reply": reply, "source": "local_knowledge"})

        # Fire up a session tracking automated tool executions
        # NEW CRASH-PROOF SERVERLESS CODE BLOCK:
        chat_session = model.start_chat(enable_automatic_function_calling=True)
        response = chat_session.send_message(user_message)
        reply = response.text

        try:
        # Try saving locally, but catch the error if the filesystem is read-only
          kb.add_conversation(user_message, reply)
        except Exception:
         pass  # Silently bypass Vercel's write-block restrictions!

        return jsonify({"reply": reply, "source": "gemini-free-plus"})

    except Exception as e:
        return jsonify({"reply": f"System Error: {str(e)}"}), 500


# Just leave it completely blank at the bottom, or use this safe fallback block:
if __name__ == '__main__':
    app.run()