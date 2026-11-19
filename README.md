# Customer Support Agent

A customer support chatbot built with Google Vertex AI (Gemini) and function calling. The agent looks up customers, orders, and tickets in a SQLite database by calling Python functions that the model chooses to use.

## How it works

1. A customer sends a message to the `/chat` endpoint.
2. Gemini reads the message and decides whether it needs data.
3. If it does, Gemini requests a function such as `lookup_customer`.
4. `app/tools.py` runs that function, which queries SQLite through `app/database.py`.
5. The result goes back to Gemini, which writes the final reply.

## Project structure

```
app/
  config.py     Reads settings from .env
  database.py   SQLite connection, tables, and queries
  tools.py      Python functions and their Gemini declarations
  agent.py      Gemini model and the tool-call loop
  main.py       Flask /chat endpoint
data/
  seed.sql      Sample customers, orders, and tickets
tests/
  test_tools.py Basic tests
```

## Setup

Run every command from the project root.

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate        (Windows: venv\Scripts\activate)
   ```
2. Install the packages:
   ```
   pip install -r requirements.txt
   ```
3. Copy the example settings and edit them:
   ```
   cp .env.example .env
   ```
   Set `GCP_PROJECT_ID` to your Google Cloud project ID. Set `MODEL_NAME` to an exact Gemini model ID that your project can use, as shown in Vertex AI Model Garden.
4. Authenticate with Google Cloud:
   ```
   gcloud auth application-default login
   ```
5. Load the sample data:
   ```
   python -c "from app.database import load_seed; load_seed()"
   ```

## Run

Start the server:
```
python -m app.main
```

Send a message:
```
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d "{\"session_id\": \"s1\", \"message\": \"Hi, my email is asha@example.com. What orders do I have?\"}"
```

## Run the tests

```
pytest
```

## Reset the database

Delete `data/support.db`, then run step 5 again. Each test run and each ticket created adds data, so reset when you want a clean state.

## Sample customers

| ID | Name | Email |
|----|------|-------|
| 1 | Asha Rao | asha@example.com |
| 2 | Ravi Kumar | ravi@example.com |
| 3 | Meena Iyer | meena@example.com |