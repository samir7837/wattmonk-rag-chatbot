# ⚡ Wattmonk AI Assistant
### A Multi-Context RAG Chatbot for Solar Industry Intelligence

> Intelligent document-grounded Q&A across general conversation, NEC solar code, and Wattmonk company knowledge — powered by LangChain, ChromaDB, and GPT-4o-mini.

---

## ✨ Features

- **Multi-Context Query Classification** — Automatically routes each query to the correct knowledge domain: General, NEC (National Electrical Code), or Wattmonk
- **PDF Document Ingestion & Chunking** — Parses and indexes source documents into semantically meaningful chunks
- **Vector Similarity Search** — Retrieves the most relevant document chunks using ChromaDB
- **Context-Aware Response Generation** — Grounds LLM answers in retrieved document context, reducing hallucination
- **Source Attribution** — Every answer is tagged with its source (NEC or Wattmonk)
- **Page-Number Citations** — Responses include the exact page numbers from source documents
- **Retrieved Context Preview** — Users can inspect the raw chunks used to generate each answer
- **Conversation Memory** — Maintains basic chat history within a session for follow-up questions
- **Confidence Indicator** — Displays a High or Medium confidence label based on retrieval quality

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **Backend** | Python 3.10+ |
| **LLM API** | [OpenRouter](https://openrouter.ai/) — OpenAI GPT-4o-mini |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) |
| **Embeddings** | `sentence-transformers` — `all-MiniLM-L6-v2` |
| **RAG Framework** | [LangChain](https://www.langchain.com/) |
| **Deployment** | [Streamlit Cloud](https://streamlit.io/cloud) |

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────┐
│  Query Classifier   │  ── General / NEC / Wattmonk
└─────────────────────┘
    │
    ├── General ──────────────────────────────────────────┐
    │                                                      │
    ├── NEC ──────┐                                        │
    │             ▼                                        ▼
    │    ┌──────────────────┐                  ┌──────────────────────┐
    │    │  ChromaDB Store  │                  │  Direct LLM Prompt   │
    │    │  (NEC Chunks)    │                  └──────────────────────┘
    │    └──────────────────┘
    │             │
    └── Wattmonk ─┤
                  ▼
        ┌──────────────────┐
        │  ChromaDB Store  │
        │ (Wattmonk Chunks)│
        └──────────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  Retrieved Chunks │  (Top-K by similarity)
        └──────────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  Prompt Builder  │  (Context + Chat History)
        └──────────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  GPT-4o-mini via  │
        │   OpenRouter API  │
        └──────────────────┘
                  │
                  ▼
        ┌──────────────────────────────────┐
        │           Response               │
        │  ✔ Answer  ✔ Source  ✔ Pages    │
        │  ✔ Context Preview  ✔ Confidence│
        └──────────────────────────────────┘
```

**Step-by-step flow:**
1. The user submits a query via the Streamlit chat interface
2. `classifier.py` determines the query domain — General, NEC, or Wattmonk
3. For NEC/Wattmonk queries, `retriever.py` fetches the top-K relevant chunks from ChromaDB
4. The retrieved chunks and conversation history are assembled into a structured prompt
5. The prompt is sent to GPT-4o-mini via the OpenRouter API
6. The app renders the answer along with source, page numbers, context preview, and confidence level

---

## 📁 Folder Structure

```
wattmonk-ai-assistant/
│
├── app.py                  # Main Streamlit application entry point
│
├── src/
│   ├── classifier.py       # Query classification logic (General / NEC / Wattmonk)
│   ├── retriever.py        # ChromaDB vector search and chunk retrieval
│   ├── ingest.py           # PDF parsing, chunking, and embedding pipeline
│   └── utils.py            # Shared helper functions
│
├── data/                   # Source PDF documents (NEC code, Wattmonk docs)
│
├── chroma_db/              # Persisted ChromaDB vector store
│
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites

- Python 3.10 or higher
- An [OpenRouter](https://openrouter.ai/) API key

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/wattmonk-ai-assistant.git
cd wattmonk-ai-assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.streamlit/secrets.toml` file in the project root:

```toml
OPENROUTER_API_KEY = "your-openrouter-api-key-here"
```

> ⚠️ Never commit this file to version control. Add `.streamlit/secrets.toml` to your `.gitignore`.

### 5. Ingest Documents

Place your PDF files inside the `data/` directory, then run the ingestion pipeline:

```bash
python src/ingest.py
```

This will chunk the PDFs, generate embeddings, and populate the `chroma_db/` vector store.

### 6. Run the App

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment on Streamlit Cloud

1. Push your project to a **public GitHub repository**
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in
3. Click **"New app"** and select your repository
4. Set the **main file path** to `app.py`
5. Under **"Advanced settings → Secrets"**, add:

```toml
OPENROUTER_API_KEY = "your-openrouter-api-key-here"
```

6. Click **Deploy** — your app will be live within minutes

> **Note:** Do not include the `chroma_db/` folder in `.gitignore` if you want the vector store to be available on deployment. Alternatively, run `ingest.py` as a startup step.

---

## 💬 Example Queries

### 🗣️ General
```
"What is RAG and how does it work?"
"Explain the difference between embeddings and fine-tuning."
```

### ⚡ NEC (National Electrical Code)
```
"What are the NEC requirements for solar PV system grounding?"
"Which NEC article covers rapid shutdown requirements for rooftop solar?"
```

### 🏢 Wattmonk
```
"What services does Wattmonk provide?"
"What is Wattmonk's typical turnaround time for permit packages?"
```

---

## 🔮 Future Improvements

- [ ] **Hybrid Search** — Combine vector similarity with keyword (BM25) search for better precision
- [ ] **Multi-document Upload** — Allow users to upload and query their own PDFs at runtime
- [ ] **Persistent Conversation Memory** — Store chat history across sessions using a database
- [ ] **Re-ranking** — Add a cross-encoder re-ranker to improve chunk relevance ordering
- [ ] **Authentication** — Add user login for personalized sessions and usage tracking
- [ ] **Streaming Responses** — Stream LLM output token-by-token for a more responsive feel
- [ ] **Evaluation Dashboard** — Add retrieval and answer quality metrics using RAGAS

---

## 👤 Author

**Samir** — *University Institute of Computing, Chandigarh University*

> Built as part of an applied AI internship project exploring production-grade RAG systems for the solar energy domain.

---

## 📄 License

This project is intended for academic and internship demonstration purposes.

---

<p align="center">Made with ☀️ and 🤖 | Powered by LangChain · ChromaDB · OpenRouter</p>
