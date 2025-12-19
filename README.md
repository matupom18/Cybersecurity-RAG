# Cybersecurity RAG System

This project is a Retrieval-Augmented Generation (RAG) system capable of answering cybersecurity-related questions using **only** the specified dataset.

## Features
- **Strict Dataset Grounding**: Answers are derived solely from the provided PDF documents.
- **Document Processing**: Uses **Docling** for high-quality PDF to Markdown conversion.
- **Orchestrator**: Uses **LangGraph** to manage the retrieval and generation workflow.
- **Vector Store**: Uses **ChromaDB** for storing and retrieving embeddings.
- **API**: **FastAPI** backend for ingestion and querying.
- **LLM Support**: Configurable for **OpenAI** (default) or **Ollama** (local).

## Prerequisites
- Python 3.10+
- OpenAI API Key (optional, defaults to OpenAI in config) OR Ollama installed and running.

## Installation

1.  **Clone the repository** (or unzip the project).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    Create a `.env` file in the root directory (optional but recommended for keys):
    ```env
    OPENAI_API_KEY=sk-your-key-here
    # If using Ollama, ensure LLM_PROVIDER="ollama" in app/config.py or set via env if supported (currently defaults to openai)
    ```

## Usage

### 1. Start the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`

### 2. Ingest Documents
The first time you run the system, you must ingest the documents from the `dataset/` folder.
```bash
curl -X POST http://localhost:8000/ingest
```

### 3. Ask a Question
```bash
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is Broken Access Control according to OWASP?"}'
```

## Architecture
1.  **Ingestion**: `DocumentLoader` reads PDFs using `docling`, chunks them, and stores embeddings in `ChromaDB`.
2.  **Retrieval**: `VectorDB` retrieves relevant chunks based on semantic similarity.
3.  **Generation**: `LangGraph` orchestrates the flow:
    - **Retrieve Node**: Fetches context.
    - **Generate Node**: Calls the LLM with a strict system prompt to use only the provided context.
4.  **Response**: Returns the answer and citations.

## Testing
Run the provided test script:
```bash
python test_rag.py
```
