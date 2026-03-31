import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

from src.retriever import retrieve_documents
from src.classifier import classify_query

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Wattmonk AI Assistant",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("❌ OPENROUTER_API_KEY not found in .env file")
    st.stop()

# -----------------------------
# Cache OpenRouter client
# -----------------------------
@st.cache_resource(show_spinner=False)
def get_openrouter_client():
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

client = get_openrouter_client()

MODEL_NAME = "openai/gpt-4o-mini"

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("⚙️ Settings")
    st.info(MODEL_NAME)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Multi-Context RAG Enabled")
    st.caption("NEC + Wattmonk + General Chat")

# -----------------------------
# Header
# -----------------------------
st.title("⚡ Wattmonk AI Assistant")
st.caption("Now supports NEC + Wattmonk knowledge")

# -----------------------------
# Initialize chat history
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey! I can now answer from NEC and Wattmonk docs 🚀"
        }
    ]

# -----------------------------
# Display previous chat messages
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# Chat input
# -----------------------------
prompt = st.chat_input("Ask anything...")

if prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # -----------------------------
    # Classify query
    # -----------------------------
    intent = classify_query(prompt)

    # -----------------------------
    # Retrieve documents
    # -----------------------------
    retrieved_docs = []
    context = ""
    source_used = None

    if intent == "NEC":
        retrieved_docs = retrieve_documents(prompt, source_name="NEC")
        source_used = "NEC"
    elif intent == "WATTMONK":
        retrieved_docs = retrieve_documents(prompt, source_name="WATTMONK")
        source_used = "WATTMONK"

    if retrieved_docs:
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # -----------------------------
    # Extract page numbers + filenames
    # -----------------------------
    page_numbers = []
    file_names = []

    for doc in retrieved_docs:
        page = doc.metadata.get("page", None)
        file_name = doc.metadata.get("file_name", "Unknown File")

        if page is not None:
            page_numbers.append(page + 1)

        file_names.append(file_name)

    unique_pages = sorted(list(set(page_numbers)))
    unique_files = sorted(list(set(file_names)))

    # -----------------------------
    # Confidence estimate
    # -----------------------------
    if retrieved_docs:
        confidence = "Medium"
        if len(retrieved_docs) >= 3:
            confidence = "High"
    else:
        confidence = "General"

    # -----------------------------
    # Build better system prompt
    # -----------------------------
    system_prompt = f"""
You are a professional AI assistant for Wattmonk.

Behavior rules:
1. If retrieved context is provided, answer primarily using that context.
2. You are allowed to summarize and explain the context clearly in your own words.
3. If the context is partially relevant, give the best grounded answer possible instead of refusing too quickly.
4. Only say "I couldn’t find that in the provided documents." if the retrieved context is clearly unrelated or empty.
5. Do NOT mention "based on context" or "source" inside your answer.
6. Keep answers clean, professional, and easy to read.
7. Prefer bullet points for technical/company-specific answers when helpful.
8. If the user asks a general conversational question and no context is retrieved, answer naturally.

Retrieved Context:
{context}
"""

    messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # -----------------------------
    # Generate response
    # -----------------------------
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=0.2
                )

                reply = response.choices[0].message.content.strip()

            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            # -----------------------------
            # Display answer
            # -----------------------------
            st.markdown(reply)

            # -----------------------------
            # Better source / citation box
            # -----------------------------
            if retrieved_docs and source_used:
                st.markdown("---")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.success(f"📚 Source: {source_used}")

                with col2:
                    if unique_pages:
                        pages_text = ", ".join(map(str, unique_pages[:10]))
                        if len(unique_pages) > 10:
                            pages_text += "..."
                        st.info(f"📄 Pages: {pages_text}")

                with col3:
                    if confidence == "High":
                        st.success(f"🎯 Confidence: {confidence}")
                    elif confidence == "Medium":
                        st.warning(f"🎯 Confidence: {confidence}")
                    else:
                        st.info(f"🎯 Confidence: {confidence}")

                if unique_files:
                    st.caption(f"Files used: {', '.join(unique_files)}")

                # -----------------------------
                # Retrieved context preview
                # -----------------------------
                with st.expander("🔍 Retrieved Context Preview"):
                    for i, doc in enumerate(retrieved_docs, start=1):
                        preview_page = doc.metadata.get("page", None)
                        preview_file = doc.metadata.get("file_name", "Unknown File")

                        if preview_page is not None:
                            preview_page = preview_page + 1

                        st.markdown(f"### Chunk {i}")
                        st.markdown(f"**File:** {preview_file}")
                        if preview_page is not None:
                            st.markdown(f"**Page:** {preview_page}")

                        preview_text = doc.page_content.strip()

                        if len(preview_text) > 1000:
                            preview_text = preview_text[:1000] + "..."

                        st.code(preview_text, language="text")
                        st.markdown("---")

    # -----------------------------
    # Save assistant response
    # -----------------------------
    st.session_state.messages.append({"role": "assistant", "content": reply})