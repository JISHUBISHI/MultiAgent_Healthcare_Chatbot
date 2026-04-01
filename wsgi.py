import os
from dotenv import load_dotenv

load_dotenv()

from healthbuddy.app import app

if __name__ == "__main__":
    # For local development only. In production (Render), Gunicorn will be used and will ignore this block.
    # Start command for production: gunicorn --bind 0.0.0.0:$PORT wsgi:app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
