from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import streamlit as st

CHROMA_DIR = "chroma_db"

@st.cache_resource(show_spinner=False)
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

@st.cache_resource(show_spinner=False)
def get_vectorstore():
    embedding_model = get_embedding_model()
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model
    )

def expand_query(query: str, source_name: str = None) -> str:
    q = query.lower().strip()

    if source_name == "NEC":
        if "article 690" in q:
            return query + " NEC Article 690 Solar Photovoltaic Systems"
        if "article 250" in q:
            return query + " NEC Article 250 Grounding and Bonding"
        if "grounding" in q:
            return query + " NEC grounding bonding requirements"
        if "disconnect" in q:
            return query + " NEC disconnect requirements solar PV"

    if source_name == "WATTMONK":
        if "services" in q:
            return query + " Wattmonk company services proposals plansets PTO"
        if "pto" in q:
            return query + " Wattmonk PTO interconnection application"

    return query

def retrieve_documents(query: str, source_name: str = None, k: int = 4):
    try:
        vectorstore = get_vectorstore()
        improved_query = expand_query(query, source_name)

        if source_name:
            docs = vectorstore.max_marginal_relevance_search(
                query=improved_query,
                k=k,
                fetch_k=8,
                filter={"source_name": source_name}
            )
        else:
            docs = vectorstore.max_marginal_relevance_search(
                query=improved_query,
                k=k,
                fetch_k=8
            )

        return docs

    except Exception as e:
        print(f"Retriever Error: {e}")
        return []