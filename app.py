import streamlit as st
import fitz
import google.generativeai as genai

st.set_page_config(page_title="SecureDocs AI Portal", page_icon="🔐", layout="wide")

st.markdown("""
<style>
  .main { background-color: #f5f7fa; }
  .stButton>button { background-color: #4a6cf7; color: white; border-radius: 8px; padding: 10px 20px; border: none; width: 100%;}
  .login-box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; }
  .header { background: linear-gradient(90deg, #4a6cf7, #6a1b9a); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

USERS = {"admin": {"password": "admin123", "role": "Admin"}, "employee": {"password": "user123", "role": "User"}}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title("🔐 SecureDocs AI")
        st.subheader("AI-Powered Secure Document Search Portal")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Secure Login"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = USERS[username]["role"]
                st.rerun()
            else:
                st.error("Ghalat username ya password")
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("Demo: admin / admin123 | employee / user123")
    st.stop()

st.markdown(f'<div class="header"><h2>Welcome, {st.session_state.username} ({st.session_state.role})</h2><p>Upload documents and ask AI questions securely.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📤 Document Upload Portal")
    api_key = st.text_input("Gemini API Key (free)", type="password")
    uploaded_files = st.file_uploader("Upload PDF Documents", type=["pdf"], accept_multiple_files=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

if api_key:
    genai.configure(api_key=api_key)

doc_text = ""
if uploaded_files:
    st.success(f"{len(uploaded_files)} documents uploaded!")
    for pdf in uploaded_files:
        if st.session_state.role == "User" and "salary" in pdf.name.lower():
            st.warning(f"Access Denied: {pdf.name} is restricted.")
            continue
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
                model = genai.GenerativeModel('gemini-1.5-flash')
                full_prompt = f"Answer ONLY from this document context:\n\n{doc_text[:15000]}\n\nQuestion: {prompt}"
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
