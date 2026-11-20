"""Flask web server exposing the support agent through a /chat endpoint."""

from flask import Flask, request, jsonify

from app.database import init_db
from app.agent import new_chat, ask_agent

app = Flask(__name__)

# Create the database tables when the server starts (safe to run repeatedly)
init_db()

# Keeps one chat session per session_id while the server is running
sessions = {}


@app.route("/", methods=["GET"])
def home():
    """Explain where the chat UI lives, since this is the API server."""
    return jsonify({
        "message": "Backend is running. Open the chat UI at http://localhost:5173"
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
