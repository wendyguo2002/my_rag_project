from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import chromadb

# 1. Set up Local Brain (Ollama) and Local Embeddings
Settings.llm = Ollama(
    model="llama3.2", 
    request_timeout=300.0,  # Increase to 5 minutes
    temperature=0.1        # Keep it low for factual resume answers
)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 2. Connect to the stored database
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_collection("portfolio_collection")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
index = VectorStoreIndex.from_vector_store(vector_store)

# 3. CUSTOM SYSTEM PROMPT (The "Persona")
# This tells the AI how to behave
SYSTEM_PROMPT = (
    "You are a helpful Career Assistant for a Software Engineer. "
    "Use the provided context to answer questions about their projects. "
    "Always focus on Technical Actions and Quantifiable Results. "
    "If asked about a challenge, use the STAR method (Situation, Task, Action, Result)."
)

query_engine = index.as_query_engine(system_prompt=SYSTEM_PROMPT)

# 4. Ask a Test Question
question = "Tell me about a time you handled a technical conflict between teams."
print(f"\nQuestion: {question}")

response = query_engine.query(question)
print("\n--- AI RESPONSE ---")
print(response)