import os
import requests
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import google.generativeai as genai
from knowledge_base import KnowledgeBase

load_dotenv()
app = Flask(__name__)
kb = KnowledgeBase()

# 1. SETUP THE FREE GOOGLE API CLIENT
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in your .env file!")

genai.configure(api_key=api_key)


# ==========================================
# REAL-TIME WEATHER HOOKS (Python Functions)
# ==========================================
def get_lat_long(city_name: str):
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


# UPDATE TO THE CORRECT FREE TIER MODEL
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",  # Swapped from 1.5 to 2.5
    tools=[get_live_weather]        
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
        # Check local knowledge base first to preserve your free tier limits
        learned_match = kb.get_learned_response(user_message)
        if learned_match:
            reply = learned_match["response"]
            kb.add_conversation(user_message, reply)
            return jsonify({"reply": reply, "source": "local_knowledge"})

        # Initialize a fresh chat session for tracking tool actions
        chat_session = model.start_chat(enable_automatic_function_calling=True)
        
        # Send message to Gemini (it handles running the weather function completely on its own!)
        response = chat_session.send_message(user_message)
        reply = response.text

        # Save successful chat data locally
        kb.add_conversation(user_message, reply)
        return jsonify({"reply": reply, "source": "gemini-free"})

    except Exception as e:
        return jsonify({"reply": f"System Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)