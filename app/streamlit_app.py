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

# Sidebar navigation
if st.session_state.jwt:
    page = "Chat"
    if st.session_state.username == "admin":
        page = st.sidebar.radio("Go to", ["Chat", "Admin Upload"])
    else:
        st.sidebar.write("You are not admin.")

    if page == "Chat":
        # Only show upload section if admin
        if st.session_state.username == "admin":
            with st.expander("Upload PDF(s) to Knowledge Base"):
                uploaded_files = st.file_uploader("Choose PDF(s)", type=["pdf"], accept_multiple_files=True)
                if uploaded_files:
                    for file in uploaded_files:
                        kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge_base"))
                        file_path = os.path.join(kb_dir, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        st.success(f"Uploaded {file.name} to knowledge_base/")
                        headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
                        resp = requests.post(f"{API_URL}/index_pdfs", headers=headers)
                        if resp.status_code == 200:
                            st.success("PDFs re-indexed!")
                        else:
                            st.error(f"Indexing failed: {resp.text}")
            with st.expander("Add Web Page as Knowledge"):
                url = st.text_input("Enter URL", key="user_url")
                if st.button("Add URL", key="user_add_url") and url:
                    headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
                    resp = requests.post(f"{API_URL}/add_url", json={"url": url}, headers=headers)
                    if resp.status_code == 200:
                        st.success("URL added and indexed!")
                    else:
                        st.error(f"Failed to add URL: {resp.text}")

        st.subheader("Chat with your PDFs")
        def send_message():
            user_input = st.session_state["input"]
            if user_input:
                headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
                resp = requests.post(f"{API_URL}/chat", json={"message": user_input}, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.history.append(("You", user_input))
                    st.session_state.history.append(("Bot", data["response"]))
                    st.session_state["input"] = ""
                else:
                    st.error(f"Error: {resp.text}")

        st.text_input("Your question", key="input")
        st.button("Send", on_click=send_message)

        for speaker, text in st.session_state.history:
            st.markdown(f"**{speaker}:** {text}")

        # Optionally, show context
        if st.session_state.history and "context" in locals() and "context" in data:
            st.markdown("---")
            st.markdown("**Context used:**")
            st.code(data["context"])

    elif page == "Admin Upload":
        st.header("Admin: Upload Knowledge")
        st.write("Only admin can access this page.")

        # PDF upload
        with st.expander("Upload PDF(s) to Knowledge Base"):
            uploaded_files = st.file_uploader("Choose PDF(s)", type=["pdf"], accept_multiple_files=True)
            if uploaded_files:
                for file in uploaded_files:
                    # (reuse your upload_pdf function here)
                    kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge_base"))
                    file_path = os.path.join(kb_dir, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    st.success(f"Uploaded {file.name} to knowledge_base/")
                    headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
                    resp = requests.post(f"{API_URL}/index_pdfs", headers=headers)
                    if resp.status_code == 200:
                        st.success("PDFs re-indexed!")
                    else:
                        st.error(f"Indexing failed: {resp.text}")

        # URL upload
        with st.expander("Add Web Page as Knowledge"):
            url = st.text_input("Enter URL", key="admin_url")
            if st.button("Add URL", key="admin_add_url") and url:
                headers = {"Authorization": f"Bearer {st.session_state.jwt}"}
                resp = requests.post(f"{API_URL}/add_url", json={"url": url}, headers=headers)
                if resp.status_code == 200:
                    st.success("URL added and indexed!")
                else:
                    st.error(f"Failed to add URL: {resp.text}")
else:
    st.sidebar.write("Please log in to access the app.")
