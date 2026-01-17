import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import MarkdownNodeParser

# 1. Setup the Embedding Model (Free/Local)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 2. Load the project markdown
print("Reading your data folder...")
reader = SimpleDirectoryReader("./data")
documents = reader.load_data()

# 3. Parse specifically for Markdown (keeps sections together)
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# 4. Create the local Database folder
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("portfolio_collection")

# 5. Connect and Index
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

print("Vectorizing your projects... this creates the 'chroma_db' folder.")
index = VectorStoreIndex(
    nodes, 
    storage_context=storage_context, 
    embed_model=embed_model
)

print("Success! Data is now stored as vectors.")