import streamlit as st
import chromadb
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

# --- PAGE CONFIG ---
st.set_page_config(page_title="Wendy's Career AI", page_icon="👩‍💻")
st.title("💬 Wendy's Technical Career Advocate")
st.markdown("---")

# 1. Optimized Model & Engine Setup
@st.cache_resource
def get_query_engine():
    # Setup Models
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = Ollama(model="llama3.2", request_timeout=300.0, temperature=0.1)
    
    # Connect to local ChromaDB
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_collection("portfolio_collection")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=Settings.embed_model
    )
    
    # --- THE SECRET SAUCE: THE TECHNICAL PROMPT ---
    # This forces the AI to use your specific technical details
    qa_prompt_tmpl_str = (
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "You are Wendy's Career Advocate. Given the context, answer the user's question.\n"
        "Rules:\n"
        "1. Be highly technical.\n"
        "2. Follow the STAR method: Situation, Task, Action (Technical), Result (Metrics).\n"
        "3. If the answer isn't in the context, say you don't know—don't make up generic advice.\n"
        "Query: {query_str}\n"
        "Answer: "
    )
    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

    # Build the engine
    engine = index.as_query_engine(
        similarity_top_k=5, # Increased to 5 to find more technical context
        streaming=True,
        response_mode="compact"
    )
    
    # Apply the prompt
    engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt_tmpl})
    
    return engine

query_engine = get_query_engine()

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm trained on Wendy's full project history. Ask me about her project experience!"}
    ]

# Show message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ex: Tell me about a technical challenge on the HoloLens project."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Execute streaming query
        streaming_response = query_engine.query(prompt)
        
        for text in streaming_response.response_gen:
            full_response += text
            response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})