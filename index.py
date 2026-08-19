import os
from urllib import response
import requests
from flask import Flask, jsonify, render_template, request
from groq import Groq
from dotenv import load_dotenv
from knowledge_base import KnowledgeBase

# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()

# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)

# =========================================================
# INITIALIZE KNOWLEDGE BASE
# =========================================================

kb = KnowledgeBase()

# =========================================================
# GROQ API SETUP
# =========================================================

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY is not set!")

client = Groq(api_key=groq_api_key)

# =========================================================
# WEATHER TOOL
# =========================================================

def get_lat_long(city_name: str):

    try:
        url = (
            f"https://geocoding-api.open-meteo.com/v1/search?"
            f"name={city_name}&count=1&language=en&format=json"
        )

        response = requests.get(url)
        data = response.json()

        if "results" in data and len(data["results"]) > 0:

            location = data["results"][0]

            return (
                location["latitude"],
                location["longitude"],
                location.get("name", city_name)
            )

    except Exception:
        pass

    return None, None, city_name


def get_live_weather(city: str):

    lat, lon, real_name = get_lat_long(city)

    if not lat:
        return f"Could not find location: {city}"

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )

        response = requests.get(url)
        data = response.json()

        current = data.get("current_weather", {})

        if current:

            temperature = current.get("temperature")
            windspeed = current.get("windspeed")

            return (
                f"Current weather in {real_name}: "
                f"{temperature}°C with wind speed "
                f"{windspeed} km/h."
            )

    except Exception as e:
        return f"Weather API Error: {str(e)}"

    return "Weather information unavailable."


# =========================================================
# TV SHOW TOOL
# =========================================================

def search_tv_show(show_name: str):

    try:
        url = f"https://api.tvmaze.com/singlesearch/shows?q={show_name}"

        response = requests.get(url)
        data = response.json()

        if data:

            summary = (
                data.get("summary", "")
                .replace("<p>", "")
                .replace("</p>", "")
                .replace("<b>", "")
                .replace("</b>", "")
            )

            return (
                f"Title: {data.get('name')} | "
                f"Rating: {data.get('rating', {}).get('average', 'N/A')}/10 | "
                f"Genres: {', '.join(data.get('genres', []))} | "
                f"Summary: {summary}"
            )

    except Exception:
        pass

    return f"Could not find TV show: {show_name}"


# =========================================================
# HOLIDAY TOOL
# =========================================================

def get_public_holidays(country_code: str):

    try:
        url = (
            f"https://date.nager.at/api/v3/PublicHolidays/"
            f"2026/{country_code.upper()}"
        )

        response = requests.get(url)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:

            holidays = [
                f"{holiday['date']}: {holiday['localName']}"
                for holiday in data[:5]
            ]

            return (
                f"Upcoming holidays in "
                f"{country_code.upper()}: "
                + ", ".join(holidays)
            )

    except Exception:
        pass

    return f"Could not fetch holidays for {country_code}"


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# CHAT API
# =========================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "reply": "Please send a valid message."
        }), 400

    try:

        # =================================================
        # LOCAL KNOWLEDGE BASE
        # =================================================

        learned_match = kb.get_learned_response(user_message)

        if learned_match:

            reply = learned_match["response"]

            try:
                kb.add_conversation(user_message, reply)
            except Exception:
                pass

            return jsonify({
                "reply": reply,
                "source": "local_knowledge"
            })

        # =================================================
        # WEATHER TOOL
        # =================================================

        if "weather" in user_message.lower():

            city = (
                user_message.lower()
                .replace("weather", "")
                .replace("in", "")
                .strip()
            )

            reply = get_live_weather(city)

            return jsonify({
                "reply": reply,
                "source": "weather_tool"
            })

        # =================================================
        # TV SHOW TOOL
        # =================================================

        if (
            "tv show" in user_message.lower()
            or "show" in user_message.lower()
        ):

            show = (
                user_message.lower()
                .replace("tv show", "")
                .replace("show", "")
                .strip()
            )

            reply = search_tv_show(show)

            return jsonify({
                "reply": reply,
                "source": "tv_show_tool"
            })

        # =================================================
        # HOLIDAY TOOL
        # =================================================

        if "holiday" in user_message.lower():

            country = user_message.split()[-1]

            reply = get_public_holidays(country)

            return jsonify({
                "reply": reply,
                "source": "holiday_tool"
            })

        # =================================================
        # GROQ AI RESPONSE
        # =================================================
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )


        reply = response.choices[0].message.content


        try:
            kb.add_conversation(user_message, reply)
        except Exception:
            pass

        return jsonify({
            "reply": reply,
            "source": "groq-ai"
        })

    except Exception as e:

        return jsonify({
            "reply": f"System Error: {str(e)}"
        }), 500


# =========================================================
# RUN FLASK APP
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)

