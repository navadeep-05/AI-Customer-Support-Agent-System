"""Flask web server exposing the support agent through a /chat endpoint."""

from flask import Flask, request, jsonify
from flask_cors import CORS

from app.database import load_seed
from app.agent import new_chat, ask_agent

app = Flask(__name__)
# Enable CORS for all origins so frontend on Render / Vercel / Netlify can connect
CORS(app)

# Seed data (also calls init_db internally) when the server starts
load_seed()

# Keeps one chat session per session_id while the server is running
sessions = {}


@app.route("/", methods=["GET"])
def home():
    """Health & info endpoint for root deployment check."""
    return jsonify({
        "status": "healthy",
        "service": "Customer Support Agent Backend API",
        "endpoints": {
            "health": "/health",
            "chat": "POST /chat"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    """Simple check that the server is running."""
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    """Handle one customer message.

    Request JSON:
        session_id (str, optional): Identifies the conversation. Defaults to "default".
        message (str, required): The customer's message.
        api_key (str, optional): User-supplied Groq API key from UI.

    Returns:
        JSON with session_id and the agent's reply.
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "default")
    message = (data.get("message") or "").strip()
    api_key = (data.get("api_key") or "").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    # Start a new chat the first time we see this session
    if session_id not in sessions:
        sessions[session_id] = new_chat()

    try:
        reply = ask_agent(sessions[session_id], message, api_key=api_key)
    except Exception as exc:
        # Reset the session so the next message starts fresh
        sessions.pop(session_id, None)
        return jsonify({"error": f"Agent error: {exc}"}), 500
    return jsonify({"session_id": session_id, "reply": reply})


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
