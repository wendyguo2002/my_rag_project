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
system_prompt=(
    "You are a Senior Technical Interview Coach. Wendy is the candidate.\n"
    "Your goal: Provide a high-impact STAR answer using ONLY the provided context.\n\n"
    "CRITICAL RULES:\n"
    "1. METRICS FIRST: If you find numbers (latency, %, time saved), you MUST include them.\n"
    "2. NO GENERALITIES: Instead of 'performance tools', say the specific tool (e.g., 'Cython' or 'Unity Profiler').\n"
    "3. FORMAT: Use bold headers for **SITUATION**, **TASK**, **ACTION**, and **RESULT**.\n"
    "4. ACCURACY: If a specific metric isn't in the context, do not invent one."
)

# 1. Create a specialized Query Engine
query_engine = index.as_query_engine(
    similarity_top_k=5,  # Look at 5 chunks instead of 2 for more detail
    system_prompt=(
        "You are Wendy's Career Advocate. Your goal is to provide highly specific "
        "interview answers using the STAR method. \n"
        "RULES:\n"
        "1. Use EXACT technical names (e.g., 'Cython', 'HoloLens', 'ChromaDB').\n"
        "2. Include specific METRICS (e.g., '0.8ms', '40% reduction') if they exist.\n"
        "3. If the context doesn't have the answer, say 'I don't have that specific data'.\n"
        "4. Format clearly with SITUATION, TASK, ACTION, RESULT headers."
    )
)

# 2. Run the Query
question = "Tell me about a time you handled a technical conflict between teams."
response = query_engine.query(question)

# 3. Print the Result with Sources
print("\n" + "="*30)
print("CAREER ADVOCATE RESPONSE:")
print("="*30)
if response.source_nodes:
    top_node = response.source_nodes[0]
    print(f"\n🏆 TOP MATCH CONFIDENCE: {top_node.score:.4f}")
    print(f"📄 EXCERPT: {top_node.node.get_content()[:200]}...")
print(response)

print("\n" + "-"*30)
print("SOURCES USED:")
for node in response.source_nodes:
    # This prints the filename and the 'confidence' score (distance)
    file_name = node.node.metadata.get('file_name', 'Unknown')
    print(f"📍 File: {file_name} (Relevance: {node.score:.2f})")
print("-"*30)