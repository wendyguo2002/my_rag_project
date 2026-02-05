# Local-RAG Career Assistant 🤖💼

A private, local RAG system to help you prep for behavioral interviews using your own project notes. Ask questions, get STAR-formatted answers with real metrics from your past work.

> **Universal Template:** Replace files in `/data` with your own notes to create your personalized interview robot.

---

## 🚀 Quick Start

### 1. Install Ollama & Pull Model
```bash
# Download from ollama.com, then:
ollama pull llama3.2
```

### 2. Setup Environment
```bash
git clone <your-repo>
cd <repo-name>

conda create -n rag_env python=3.11
conda activate rag_env
pip install -r requirements.txt
```

### 3. Run
```bash
python ingest.py      # Index your data
streamlit run app.py  # Launch interface
```

---

## 🛠️ Tech Stack

- **LLM:** Llama 3.2 (via Ollama)
- **RAG:** LlamaIndex
- **Vector DB:** ChromaDB
- **Embeddings:** `BAAI/bge-small-en-v1.5`
- **UI:** Streamlit

---

## 🤖 Make It Yours

1. **Clear demo data:**
```bash
   rm -rf chroma_db/
   rm data/*.md
```

2. **Add your `.md` files to `/data`**
   - Use clear headers for better chunking
   - Include metrics, technologies, STAR stories
   
3. **Re-index:**
```bash
   python ingest.py
   streamlit run app.py
```

---

## 📁 Structure
```
project/
├── app.py              # Streamlit UI
├── ingest.py           # Data indexing
├── requirements.txt    # Dependencies
├── data/               # Your markdown files
└── chroma_db/          # Vector database (auto-generated)
```

---

## 💡 Example Questions

- "Tell me about a time you optimized performance"
- "Describe your experience with distributed systems"
- "What was your most challenging debugging experience?"
- "Give an example of when you disagreed with a teammate"

---

## ⚙️ Configuration

**Adjust retrieval count** (`app.py`):
```python
retriever = index.as_retriever(similarity_top_k=5)  # Change to 3-10
```

**Change model:**
```bash
ollama pull llama3.1
# Update app.py: Settings.llm = Ollama(model="llama3.1")
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Ollama not responding" | Run `ollama serve` |
| ChromaDB locked | `rm chroma_db/chroma.sqlite3-wal` |
| Out of memory | Use smaller model: `ollama pull llama3.2:1b` |
| Slow responses | Reduce `similarity_top_k` to 3 |

---

## 📊 Requirements

- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** ~5GB for models
- **OS:** macOS, Linux, Windows

---

## 📄 License

MIT License - use freely for interview prep!

---

**Made with ❤️ for software engineers. Star ⭐ if this helped you!**