import streamlit as st
import fitz
from google import genai

st.set_page_config(page_title="Chat with your Documents")
st.title("📄 Chat with your Documents")

api_key = st.sidebar.text_input("Gemini API Key (free)", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

uploaded_files = st.sidebar.file_uploader("PDF upload karo", type="pdf", accept_multiple_files=True)

doc_text = ""
if uploaded_files:
    for pdf in uploaded_files:
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        for page in doc:
            doc_text += page.get_text()

st.header("💬 Chat with your Documents")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        if not api_key:
            st.warning("Pehle sidebar me Gemini API Key dalo.")
        elif not doc_text:
            st.warning("Pehle koi PDF upload karo.")
        else:
            with st.spinner("AI parh raha hai..."):
                full_prompt = f"Answer ONLY from this document context:\n\n{doc_text[:15000]}\n\nQuestion: {prompt}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
