import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.utils import get_text_splitter

# -----------------------------
# Paths
# -----------------------------
DATA_DIR = "data"
CHROMA_DIR = "chroma_db"

# -----------------------------
# Embedding model
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# Helper to load and split PDFs
# -----------------------------
def load_and_split_pdf(file_path, source_name):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Add metadata
    for doc in documents:
        doc.metadata["source_name"] = source_name
        doc.metadata["file_name"] = os.path.basename(file_path)

    splitter = get_text_splitter()
    chunks = splitter.split_documents(documents)
    return chunks

# -----------------------------
# Main ingestion function
# -----------------------------
def ingest_documents():
    all_docs = []

    files = [
        ("data/nec_code.pdf", "NEC"),
        ("data/wattmonk.pdf", "WATTMONK"),
        ("data/wattmonk_info.pdf", "WATTMONK")
    ]

    for file_path, source_name in files:
        if os.path.exists(file_path):
            print(f"Loading: {file_path}")
            docs = load_and_split_pdf(file_path, source_name)

            # Limit NEC chunks to avoid huge processing load
            if source_name == "NEC":
                docs = docs[:1500]
                print(f"Limited NEC chunks to: {len(docs)}")

            print(f"Chunks from {source_name}: {len(docs)}")
            all_docs.extend(docs)
        else:
            print(f"File not found: {file_path}")

    if not all_docs:
        print("No documents found to ingest.")
        return

    print(f"\nTotal chunks created: {len(all_docs)}")

    # Store in ChromaDB
    print("Creating Chroma vector store... this may take a few minutes.")
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )

    vectorstore.persist()
    print("✅ Documents successfully ingested into ChromaDB")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    ingest_documents()