# 🧠 SlackMind — Intelligent Slack Knowledge Base (ISKB)

SlackMind bridges the gap between institutional knowledge silos (PDFs, URLs, local documents) and your primary communication workspace on Slack. By integrating a retrieval-augmented generation (RAG) backend powered by Google Gemini and ChromaDB/Pinecone with a modern React admin dashboard, SlackMind allows team members to query, search, and summarize workspace files instantly without leaving Slack.

---

## 🚀 Key Features

*   **Multi-Format Ingestion Engine**: Parse and ingest text from `.pdf`, `.docx`, `.txt` files, and raw web URLs.
*   **A.I. Auto-Tagging**: Documents are automatically analyzed during upload by Gemini to extract relevant tags for categorization.
*   **Natural Language Workspace Q&A**: Simply `@mention` the bot in any channel or DM to query the knowledge base.
*   **Deterministic Citations**: Answers include a `Sources Used:` list to ensure all responses are grounded and verifiable.
*   **Slack Commands**:
    *   `/summarize [document_name]`: Instantly generate 3-5 bullet-point key takeaways of any document.
    *   `/ingest-url [url]`: Index web page content directly from Slack.
    *   `/ingest-thread [thread_ts]`: Archive a discussion thread into the team's knowledge base.
*   **Security Access Control**: Mapped knowledge scopes (`Org` wide, channel-based `Team`, or individual `Private` user scope).
*   **Sleek Management Dashboard**: Real-time React dashboard for uploading files, monitoring indexing progress, and searching the database.

---

## 🛠️ Tech Stack

*   **Frontend**: React (Vite), styled with clean, responsive modern CSS.
*   **Backend Orchestrator**: FastAPI (Python 3.10+) for asynchronous webhook handling and REST APIs.
*   **AI Models**:
    *   **LLM**: Google Gemini (`gemini-2.5-flash` / `gemini-3.1-flash-lite` for auto-tagging).
    *   **Embeddings**: Google Generative AI Embeddings (`models/text-embedding-004`).
*   **Vector Database**: ChromaDB (local persistent vector store) / Pinecone (Serverless cloud option).
*   **Slack Integration**: Slack Bolt framework.

---

## 📐 Architecture & Workflow

```mermaid
graph TD
    A[React Admin Dashboard] -->|API: Upload File / URL| B(FastAPI Server)
    C[Slack Workspace] -->|Mentions / Slash Commands| B
    B -->|Ingestion & Chunking| D[LangChain Pipeline]
    D -->|Generate Embeddings| E[Google Gemini API]
    D -->|Upsert Chunks & Metadata| F[ChromaDB / Pinecone]
    F -->|Semantic Similarity Search| B
    B -->|Grounded AI Response| C
```

---

## 🔐 Security & Repository Cleanliness

We enforce strict data protection and security scanning policies:
*   **Zero Credentials Hardcoding**: All secrets and API keys (Google Gemini, Slack tokens) are kept strictly out of the code and read dynamically from `.env` using environment variables.
*   **Pre-configured `.gitignore`**: The root configuration blocks pushing local configurations and dependencies (`.env`, `.venv/`, `chroma_db/`, and `node_modules/`) to remote source control.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
Ensure you have the following installed:
*   Python 3.10+
*   Node.js (v18+)
*   `ngrok` (for forwarding Slack webhooks to local server)

### 2. Environment Configuration
Create a `.env` file in the root folder of the project with the following keys:
```env
# Google Gemini Configuration
GOOGLE_API_KEY=your_gemini_api_key_here

# Vector DB Configuration (defaults to 'chroma')
VECTOR_DB_PROVIDER=chroma

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token
```

### 3. Backend Setup
Navigate to the root directory and install Python dependencies:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run the FastAPI server
uvicorn backend.main:app --reload
```
The backend will run on `http://127.0.0.1:8000`.

### 4. Public Tunnel Setup
Run `ngrok` to expose your local port:
```bash
ngrok http 8000
```
Copy the forwarding HTTPS URL (e.g. `https://xxxx.ngrok-free.app`).

### 5. Slack Bot Setup
1. Go to [Slack API Dashboard](https://api.slack.com/apps) and create a new App.
2. Under **OAuth & Permissions**, add these bot scopes:
    *   `app_mentions:read`
    *   `chat:write`
    *   `commands`
3. Under **Event Subscriptions**:
    *   Toggle **Enable Events** to On.
    *   Paste your `ngrok` URL with the `/slack/events` path: `https://xxxx.ngrok-free.app/slack/events`
    *   Subscribe to the bot event: `app_mention`.
4. Under **Slash Commands**, register the following:
    *   `/summarize`
    *   `/ingest-url`
    *   `/ingest-thread`
5. Install the app to your workspace and copy the Bot Token and Signing Secret into your `.env`.

### 6. Frontend Setup
Navigate to the `frontend/` directory, install packages, and start the development server:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📋 Hackathon Evaluation Benchmarks

| Metric | Baseline State | SlackMind Target |
| :--- | :--- | :--- |
| **Response Generative Accuracy** | General Knowledge / Hallucinations | $\ge 80\%$ Grounded, Factually Verifiable Outputs |
| **Operational Latency** | Manual search: Minutes to Hours | AI Semantic Retrieval: $< 5\text{s}$ |
| **Enterprise Data Scope** | Siloed local/personal drives | Centralized Access Layer (Org, Team, Private) |
| **Supported Media Inputs** | PDF and Text files only | Multi-source (PDF, DOCX, Web URLs, Slack Threads) |

---
*Developed during the AI Buildathon. Build with intent, solve with clarity.*
