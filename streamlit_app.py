"""
Streamlit Test App for Adaptive Second Brain
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Second Brain", page_icon="🧠", layout="wide")

# ─── Session State Initialization ───
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def auth_headers():
    """Returns Authorization header dict if logged in."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


# Top Bar: Title + Auth 
top_left, top_right = st.columns([4, 1])

with top_left:
    st.title("🧠 Adaptive Second Brain")

with top_right:
    if st.session_state.token is None:
        # Not logged in — show login/register popover 
        with st.popover("🔑 Login / Register", use_container_width=True):
            auth_tab = st.radio("Action", ["Login", "Register"], horizontal=True, label_visibility="collapsed")

            if auth_tab == "Login":
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_pw")
                if st.button("Login", use_container_width=True):
                    resp = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password})
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error(f"Login failed: {resp.json().get('detail', resp.text)}")
            else:
                first = st.text_input("First Name", key="reg_first")
                last = st.text_input("Last Name", key="reg_last")
                email = st.text_input("Email", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_pw")
                if st.button("Register", use_container_width=True):
                    resp = requests.post(f"{API_BASE}/auth/register", json={
                        "first_name": first, "last_name": last,
                        "email": email, "password": password,
                    })
                    if resp.status_code == 200:
                        st.success("Registered! Switch to Login.")
                    else:
                        st.error(f"Failed: {resp.json().get('detail', resp.text)}")
    else:
        # Logged in — show user menu 
        with st.popover(f"👤 {st.session_state.user_email}", use_container_width=True):
            st.markdown(f"**{st.session_state.user_email}**")
            if st.button("Logout", use_container_width=True):
                st.session_state.token = None
                st.session_state.user_email = None
                st.session_state.current_chat_id = None
                st.session_state.messages = []
                st.rerun()


# Not logged in — stop here 
if st.session_state.token is None:
    st.info("👆 Click **Login / Register** in the top right to get started.")
    st.stop()


#  Sidebar: Chat List 
st.sidebar.title("💬 Chats")

if st.sidebar.button("➕ New Chat", use_container_width=True, type="primary"):
    resp = requests.post(f"{API_BASE}/chat/", headers=auth_headers())
    if resp.status_code == 200:
        new_chat = resp.json()
        st.session_state.current_chat_id = new_chat["id"]
        st.session_state.messages = []
        st.rerun()

st.sidebar.divider()

# load chats list
chats_resp = requests.get(f"{API_BASE}/chat/", headers=auth_headers())
chats = chats_resp.json() if chats_resp.status_code == 200 else []

if not chats:
    st.sidebar.caption("No chats yet. Click **New Chat** to start!")
else:
    for chat in chats:
        is_active = st.session_state.current_chat_id == chat["id"]
        btn_type = "primary" if is_active else "secondary"
        if st.sidebar.button(
            f"{'💬' if is_active else '🗨️'} {chat['title']}",
            key=f"chat_{chat['id']}",
            use_container_width=True,
            type=btn_type,
        ):
            st.session_state.current_chat_id = chat["id"]
            # load messages for this chat
            msg_resp = requests.get(f"{API_BASE}/chat/{chat['id']}", headers=auth_headers())
            if msg_resp.status_code == 200:
                data = msg_resp.json()
                st.session_state.messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in data.get("messages", [])
                ]
            else:
                st.session_state.messages = []
            st.rerun()


#  No chat selected 
if st.session_state.current_chat_id is None:
    st.info("👈 Create a **New Chat** in the sidebar to get started.")
    st.stop()


#  Main Chat Area 

# Document upload bar (inside chat) 
with st.container():
    doc_col, status_col = st.columns([3, 2])

    with doc_col:
        uploaded_file = st.file_uploader(
            "📎 Upload documents for this chat",
            type=["pdf", "docx"],
            accept_multiple_files=False,
            key=f"upload_{st.session_state.current_chat_id}",
        )
        if uploaded_file and st.button("Upload & Attach to Chat"):
            with st.spinner("Uploading & processing document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                resp = requests.post(f"{API_BASE}/documents/upload", files=files, headers=auth_headers())
            if resp.status_code == 200:
                doc_data = resp.json()
                st.success(f"✅ Uploaded: **{doc_data['filename']}** (id: {doc_data['id']})")
                st.rerun()
            else:
                st.error(f"Upload failed: {resp.json().get('detail', resp.text)}")

    with status_col:
        # show documents for this user (available to attach)
        docs_resp = requests.get(f"{API_BASE}/documents/", headers=auth_headers())
        user_docs = docs_resp.json() if docs_resp.status_code == 200 else []
        ready_docs = [d for d in user_docs if d["processing_status"] == "ready"]

        if ready_docs:
            st.markdown("**📄 Available documents:**")
            for doc in ready_docs:
                st.caption(f"✅ {doc['filename']}  *(id: {doc['id']})*")
        else:
            st.caption("No documents uploaded yet. Upload one above ☝️")

# document selection for RAG queries
selected_doc_ids = []
if ready_docs:
    doc_options = {f"{d['filename']} (id:{d['id']})": d["id"] for d in ready_docs}
    selected = st.multiselect(
        "📎 Select which documents to query:",
        options=list(doc_options.keys()),
        default=list(doc_options.keys()),
    )
    selected_doc_ids = [doc_options[s] for s in selected]

st.divider()

#  Chat Messages Display 
for msg in st.session_state.messages:
    role = msg["role"]
    if "user" in str(role).lower():
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])

#  Chat Input 
if prompt := st.chat_input("Ask a question about your documents..."):
    # show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # send to API and show reponse
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{API_BASE}/chat/{st.session_state.current_chat_id}/message",
                json={"content": prompt, "document_ids": selected_doc_ids},
                headers=auth_headers(),
            )

        if resp.status_code == 200:
            ai_msg = resp.json()
            ai_content = ai_msg.get("content", "No response")
            st.write(ai_content)
            st.session_state.messages.append({"role": "ai", "content": ai_content})
        else:
            error_msg = f"Error: {resp.json().get('detail', resp.text)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "ai", "content": error_msg})
