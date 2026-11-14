
import streamlit as st
import requests
import os
import textwrap

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)

st.set_page_config(
    page_title="KeyroRent AI Assistant",
    page_icon="🚗",
    layout="wide"
)

# Session State
if "page" not in st.session_state:
    st.session_state.page = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []


# Custom CSS
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #101820, #243b55);
    color: white;
}

.header {
    text-align: center;
    padding: 20px;
    background: #162b40;
    border-radius: 15px;
    margin-bottom: 20px;
}

.header h1 {
    color: #38bdf8;
}

/* Chat message bubbles */
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
}

/* Chat message text */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] span {
    color: #102a43 !important;
}

/* Chat input box */
.stChatInput textarea {
    background-color: #ffffff !important;
    color: #102a43 !important;
    caret-color: #0284c7 !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 10px !important;
}

/* Input placeholder */
.stChatInput textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

/* Input focus */
.stChatInput textarea:focus {
    border: 2px solid #0284c7 !important;
}

</style>
""", unsafe_allow_html=True)


# HOME PAGE
if st.session_state.page == "home":

    st.image(
        "KeyroRent AI Rental Assistant.png",
        use_container_width=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        if st.button(
            "💬 Chat with KeyroRent AI",
            use_container_width=True
        ):

            st.session_state.page = "chat"
            st.rerun()


# CHATBOT PAGE
elif st.session_state.page == "chat":

    st.markdown(
        textwrap.dedent("""
        <div class="header">
            <h1>🚗 KeyroRent AI Assistant</h1>
            <p>Your Intelligent Rental Customer Support Assistant</p>
            <p>Ask your rental questions in English, Telugu or Roman Telugu.</p>
        </div>
        """),
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅ Back to Home"):
            st.session_state.page = "home"
            st.rerun()

    with col2:
        if st.button("🗑 Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # Welcome Message
    if not st.session_state.messages:

        with st.chat_message("assistant"):
            st.write(
                "Welcome to KeyroRent AI! "
                "How can I help you with your rental questions today?"
            )

    # Display Chat History
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Customer Input
    question = st.chat_input(
        "Type your rental question here..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        try:

            # Get previous conversation messages
            previous_history = st.session_state.messages[:-1]

            chat_history = [
                {
                    "role": message["role"],
                    "content": message["content"]
                }
                for message in previous_history
            ]

            # Send current question and previous conversation
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "question": question,
                    "chat_history": chat_history
                },
                timeout=60
            )

            response.raise_for_status()

            answer = response.json()["answer"]

        except requests.exceptions.RequestException:
            answer = (
                "Sorry, the chatbot service is currently unavailable. "
                "Please try again later."
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        with st.chat_message("assistant"):
            st.write(answer)
