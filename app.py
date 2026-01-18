import streamlit as st
import chromadb
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

# --- CONFIGURATION ---
st.set_page_config(page_title="Wendy's Career AI", page_icon="🤖")
st.title("💬 Wendy's Career Advocate")

# 1. This function runs ONCE and stays in RAM
@st.cache_resource
def get_query_engine():
    # Setup Models for CPU efficiency
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = Ollama(model="llama3.2", request_timeout=300.0, temperature=0.1)
    
    # Connect to ChromaDB
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_collection("portfolio_collection")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    # Create the engine with STREAMING enabled
    return index.as_query_engine(
        similarity_top_k=3,  # Fewer chunks = faster CPU processing
        streaming=True,      # This prevents the ReadTimeout error
        response_mode="compact" 
    )

query_engine = get_query_engine()

# --- CHAT UI LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask me about my HoloLens or PrairieLearn projects!"}]

# Display history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Input
if prompt := st.chat_input("Tell me about a technical conflict."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Assistant Response with Streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Start the query
        streaming_response = query_engine.query(prompt)
        
        # Pull tokens one by one
        for text in streaming_response.response_gen:
            full_response += text
            response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})