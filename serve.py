"""
Production server for the AI chatbot.
Runs the Flask app using Waitress WSGI server.
"""

import os

try:
    from waitress import serve
except ImportError:
    raise SystemExit(
        "❌ Waitress not installed.\n"
        "Run: pip install -r requirements.txt"
    )

from main import app

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 STARTING AI CHATBOT SERVER")
    print("=" * 50)
    print(f"🌐 Host: {HOST}")
    print(f"🔌 Port: {PORT}")
    print(f"📍 URL: http://127.0.0.1:{PORT}")
    print("✅ Running with Waitress Production Server")
    print("=" * 50)

    try:
        serve(app, host=HOST, port=PORT, threads=4)
    except Exception as e:
        print("❌ SERVER ERROR:")
        print(str(e))
