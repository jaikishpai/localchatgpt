import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
st.title("LocalChatGPT")

# --- Authentication ---
if "jwt" not in st.session_state:
    st.session_state.jwt = None
if "history" not in st.session_state:
    st.session_state.history = []
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Registration ---
def register(username, password):
    resp = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
    if resp.status_code == 200:
        st.success("Registration successful! Please log in.")
    else:
        st.error(f"Registration failed: {resp.text}")

def login(username, password):
    resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    if resp.status_code == 200:
        st.session_state.jwt = resp.json()["access_token"]
        st.session_state.username = username
        st.success("Logged in!")
    else:
        st.error("Login failed.")

def logout():
    st.session_state.jwt = None
    st.session_state.history = []
    st.session_state.username = ""

# --- Auth UI ---
if st.session_state.jwt:
    st.write(f"Logged in as `{st.session_state.username}`.")
    if st.button("Logout"):
        logout()
else:
    tabs = st.tabs(["Login", "Register"])
    with tabs[0]:
        with st.form("login"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login")
            if submitted:
                login(username, password)
    with tabs[1]:
        with st.form("register"):
            reg_username = st.text_input("Username", key="reg_user")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_submitted = st.form_submit_button("Register")
            if reg_submitted:
                register(reg_username, reg_password)

# --- PDF Upload & Indexing ---
def upload_pdf(file, jwt):
    # Save file to knowledge_base/ (assumes local mount)
    kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge_base"))
    file_path = os.path.join(kb_dir, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    st.success(f"Uploaded {file.name} to knowledge_base/")
    # Trigger re-indexing
    headers = {"Authorization": f"Bearer {jwt}"}
    resp = requests.post(f"{API_URL}/index_pdfs", headers=headers)
    if resp.status_code == 200:
        st.success("PDFs re-indexed!")
    else:
        st.error(f"Indexing failed: {resp.text}")

if st.session_state.jwt:
    with st.expander("Upload PDF(s) to Knowledge Base"):
        uploaded_files = st.file_uploader("Choose PDF(s)", type=["pdf"], accept_multiple_files=True)
        if uploaded_files:
            for file in uploaded_files:
                upload_pdf(file, st.session_state.jwt)

    st.subheader("Chat with your PDFs")
    user_input = st.text_input("Your question", key="input")
    if st.button("Send") and user_input:
        headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
        resp = requests.post(f"{API_URL}/chat", json={"message": user_input}, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.history.append(("You", user_input))
            st.session_state.history.append(("Bot", data["response"]))
        else:
            st.error(f"Error: {resp.text}")

    for speaker, text in st.session_state.history:
        st.markdown(f"**{speaker}:** {text}")

    # Optionally, show context
    if st.session_state.history and "context" in locals() and "context" in data:
        st.markdown("---")
        st.markdown("**Context used:**")
        st.code(data["context"])
