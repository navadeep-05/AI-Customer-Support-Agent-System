# Customer Support Agent

An intelligent customer service assistant with function calling, SQLite database integration, and high-speed Groq LPU inference.

---

## 🚀 Two-Service Deployment on Render (Frontend + Backend)

You can deploy this repository as **two separate services** on Render (both on the free tier):

### Service 1: Backend API (Render Web Service)
1. In [Render Dashboard](https://dashboard.render.com/), click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure settings:
   - **Name:** `support-agent-api`
   - **Root Directory:** Leave empty (root)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app.main:app`
   - **Plan:** `Free`
4. In **Environment Variables**, add:
   - `GROQ_API_KEY`: *(Your Groq API key)*
   - `MODEL_NAME`: `openai/gpt-oss-20b`
5. Click **Create Web Service**. Note your backend URL (e.g., `https://support-agent-api.onrender.com`).

---

### Service 2: Frontend UI (Render Static Site)
1. In Render Dashboard, click **New +** → **Static Site**.
2. Connect the same repository.
3. Configure settings:
   - **Name:** `support-agent-ui`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. In **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://support-agent-api.onrender.com` *(Replace with your real backend URL from Service 1)*
5. Click **Create Static Site**.

---

## 💻 Local Development

### 1. Run the Backend:
```bash
python -m app.main
```
Runs at `http://127.0.0.1:5000`.

### 2. Run the Frontend:
```bash
cd frontend
npm install
npm run dev
```
Runs at `http://localhost:5173`.
