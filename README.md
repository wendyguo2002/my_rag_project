# Local-RAG Career Assistant 🤖💼
A private, local Retrieval-Augmented Generation (RAG) system designed to help Software Engineers prepare for behavioral interviews using the **STAR method** (Situation, Task, Action, Result).

## 🚀 The Problem
Technical interviews often require specific metrics and "conflict resolution" stories. Manually searching through old project notes during prep is slow. This tool uses AI to instantly retrieve your actual career data and frame it for an interviewer.

## 🛠️ Tech Stack
- **LLM:** [Llama 3.2](https://ollama.com/) (Running locally via Ollama)
- **Orchestration:** [LlamaIndex](https://www.llamaindex.ai/)
- **Vector Database:** [ChromaDB](https://www.trychroma.com/)
- **Embeddings:** `BAAI/bge-small-en-v1.5` (Running locally via HuggingFace)
- **Language:** Python 3.11

## 🏗️ Architecture
1. **Ingestion:** Parses Markdown project files, chunks text by headers, and converts them into 384-dimensional vectors.
2. **Storage:** Vectors are stored in a persistent local ChromaDB instance.
3. **Retrieval:** Uses semantic search to find the most relevant project context for any interview question.
4. **Generation:** Augments the LLM prompt with retrieved context and enforces a "STAR-method" persona.

## 📦 Installation & Setup
1. **Install Ollama:** Download from [ollama.com](https://ollama.com) and run `ollama pull llama3.2`.
2. **Setup Environment:**
```bash
   conda create -n rag_env python=3.11
   conda activate rag_env
   pip install llama-index chromadb llama-index-vector-stores-chroma llama-index-embeddings-huggingface llama-index-llms-ollama
```

## 🚀 Usage

* **Add Your Data:** Place your project `.md` files in the `/data` folder.
* **Ingest Data:**
```bash
  python ingest.py
```
* **Ask Questions:**
```bash
  python query.py
```
