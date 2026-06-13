# Intelligent Slack Knowledge Base (ISKB) - Demo Script

**Total Demo Time:** 5 Minutes

## 1. The Problem (30 seconds)
"Welcome judges. Today, enterprise knowledge is trapped in silos—Google Drives, Notion pages, and long Slack threads. Employees waste hours searching, and when they do find answers, they lack verifiable citations. We built the **Intelligent Slack Knowledge Base** to solve this. It’s an enterprise-grade RAG ingestion engine that lives directly where your team works: Slack."

## 2. The Solution: Admin Dashboard & Auto-Tagging (1 minute)
*Action: Open the React Admin Dashboard (`http://localhost:5173`)*
* "Our backend has already ingested over **50 synthetic enterprise documents** spanning HR policies to technical specs."
* "Let's ingest a new document live."
* **Action:** Drag and drop a sample `.pdf` or `.docx` into the dashboard. Choose the `org` scope.
* "Notice that upon ingestion, our system doesn't just chunk and embed. We use a Gemini LLM step to **auto-tag** the document with 3 contextual keywords, making future categorization and retrieval instant."

## 3. Slack Integration & Multi-format Ingestion (1.5 minutes)
*Action: Switch to Slack*
* "Let's say our team is discussing a new competitor in a thread."
* **Action:** In a thread, type some messages about a competitor. Then use the slash command:
  `/ingest-thread [thread_timestamp]`
* "We just ingested an entire Slack thread into the vector database. We can also do the same for external documentation using `/ingest-url https://example.com`."

## 4. Multi-turn Q&A and Citations (1.5 minutes)
*Action: Stay in Slack, demonstrate RAG*
* "Now, let's query the knowledge base. We built a conversational memory buffer so you can ask follow-ups."
* **Action:** Type `@KnowledgeBot What is our paternity leave policy?`
* *Wait for response.* "Notice two things: the answer is highly specific, and it includes a **Sources Used** footnote to prevent hallucinations and build trust."
* **Action:** Type a follow-up: `@KnowledgeBot Who does it apply to?`
* "The bot remembers the context of 'paternity leave' and answers correctly."

## 5. Security & Scope (30 seconds)
* "Finally, security is built into the core. Documents can be scoped to `org`, `team_#channel`, or `user_id`. When a user asks a question, the vector DB dynamically filters the embeddings so they only retrieve context they are authorized to see."
* "This is ISKB—breaking down knowledge silos without leaving Slack."
