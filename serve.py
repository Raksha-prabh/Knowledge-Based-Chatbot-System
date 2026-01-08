"""Run the Flask app using Waitress production WSGI server.

Usage:
    python serve.py

This avoids the Flask development server warning.
"""

import os
try:
    from waitress import serve
except Exception:
    raise SystemExit("Please install dependencies: pip install -r requirements.txt")

from main import app

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    print(f"Serving on http://{host}:{port} using Waitress")
    serve(app, host=host, port=port)
