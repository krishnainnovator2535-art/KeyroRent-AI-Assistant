
import streamlit as st
from datetime import datetime
import requests
import os
import base64
import textwrap

# ==========================================
# CONFIGURATION
# ==========================================

API_URL = st.secrets.get(
    "API_URL",
    os.getenv("API_URL", "http://127.0.0.1:8000")
)

POSTER_PATH = "KeyroRent AI Rental Assistant.png"

with open(POSTER_PATH, "rb") as image_file:
    POSTER_BASE64 = base64.b64encode(
        image_file.read()
    ).decode("utf-8")


st.set_page_config(
    page_title="KeyroRent | AI Rental Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# SESSION STATE
# ==========================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# PREMIUM AUTOMOTIVE CSS
# ==========================================

st.markdown("""
<style>

/* MAIN BACKGROUND */

.stApp {
    background:
        radial-gradient(
            circle at top right,
            #1e3a5f 0%,
            transparent 40%
        ),
        linear-gradient(
            135deg,
            #07111f,
            #10243a,
            #07111f
        );

    color: #f8fafc;
}


/* REMOVE DEFAULT TOP SPACE */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}


/* GENERAL TEXT */

h1, h2, h3, p, label {
    font-family: Arial, sans-serif;
}


/* BRAND NAVIGATION */

.brand-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    padding: 18px 25px;

    background: rgba(15, 35, 58, 0.95);

    border: 1px solid rgba(56, 189, 248, 0.25);

    border-radius: 15px;

    margin-bottom: 35px;
}

.brand-name {
    color: #38bdf8;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: 1px;
}

.brand-tagline {
    color: #cbd5e1;
    font-size: 13px;
}


/* HOME HERO SECTION */

.hero-title {
    color: #ffffff;

    font-size: 48px;

    font-weight: 800;

    line-height: 1.2;

    margin-bottom: 15px;
}

.hero-title span {
    color: #38bdf8;
}

.hero-description {
    color: #cbd5e1;

    font-size: 17px;

    line-height: 1.8;

    margin-bottom: 20px;
}


/* FEATURE TAGS */

.feature-tag {
    display: inline-block;

    background: rgba(56, 189, 248, 0.12);

    color: #7dd3fc;

    border: 1px solid rgba(56, 189, 248, 0.35);

    border-radius: 20px;

    padding: 8px 14px;

    margin: 5px 5px 5px 0;

    font-size: 13px;
}


/* MAIN BUTTONS */

div[data-testid="stButton"] > button {

    background: linear-gradient(
        135deg,
        #38bdf8,
        #0284c7
    ) !important;

    color: #07111f !important;

    border: 1px solid #7dd3fc !important;

    border-radius: 12px !important;

    min-height: 48px !important;

    font-size: 15px !important;

    font-weight: 750 !important;

    box-shadow: 0 4px 15px rgba(2, 132, 199, 0.2) !important;

    transform: none !important;

    animation: none !important;

    transition: background 0.2s ease, box-shadow 0.2s ease !important;
}


/* BUTTON TEXT */

div[data-testid="stButton"] > button p,
div[data-testid="stButton"] > button span {

    color: #07111f !important;

    font-weight: 750 !important;
}


/* BUTTON HOVER */

div[data-testid="stButton"] > button:hover {

    background: linear-gradient(
        135deg,
        #7dd3fc,
        #38bdf8
    ) !important;

    box-shadow: 0 5px 20px rgba(56, 189, 248, 0.35) !important;

    transform: none !important;
}


/* REMOVE UNWANTED BUTTON MOVEMENT */

div[data-testid="stButton"] > button:active {

    transform: none !important;

    animation: none !important;
}



/* CHAT HEADER */

.chat-header {
    text-align: center;
    background: linear-gradient(135deg, #081a32, #123e63);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 20px;
    padding: 30px 20px;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.chat-header h1 {
    color: #38bdf8;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 10px;
}

.chat-header p {
    color: #dbeafe;
    font-size: 15px;
    line-height: 1.6;
}




/* COMMON CHAT MESSAGE STYLE */

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
}

/* ALL CHAT TEXT */

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li {
    color: #102a43 !important;
    line-height: 1.8 !important;
}

/* USER MESSAGE */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {
    background-color: #e0f2fe !important;
    border-left: 5px solid #0284c7 !important;
}

/* AI MESSAGE */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {
    background-color: #ffffff !important;
    border-left: 5px solid #123e63 !important;
}

/* CHAT INPUT */

.stChatInput textarea {
    background: #ffffff !important;
    color: #102a43 !important;
    caret-color: #0284c7 !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    padding: 12px !important;
}

/* INPUT PLACEHOLDER */
/* INPUT PLACEHOLDER */

.stChatInput textarea::placeholder {

    color: #64748b !important;

    opacity: 1 !important;
}


/* INPUT FOCUS */

.stChatInput textarea:focus {

    border: 2px solid #0284c7 !important;

    box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
}


/* FOOTER */

.footer {

    text-align: center;

    color: #94a3b8;

    font-size: 12px;

    padding: 25px 10px;

    margin-top: 35px;

    border-top: 1px solid rgba(148, 163, 184, 0.2);
}


/* MOBILE RESPONSIVENESS */

@media (max-width: 768px) {

    .hero-title {
        font-size: 34px;
    }

    .brand-name {
        font-size: 20px;
    }

    .chat-header h1 {
        font-size: 25px;
    }

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

}

</style>
""", unsafe_allow_html=True)


# ==========================================
# BRAND HEADER
# ==========================================

# ==========================================
# BRAND HEADER
# ==========================================

st.markdown(
    textwrap.dedent("""
    <div class="brand-header">
        <div>
            <div class="brand-name">🚗 KEYRORENT</div>
            <div class="brand-tagline">
                Intelligent Rental Customer Support
            </div>
        </div>
        <div class="brand-tagline">
            AI POWERED ASSISTANT
        </div>
    </div>
    """),
    unsafe_allow_html=True
)

# ==========================================
# HOME PAGE
# ==========================================


if st.session_state.page == "home":

    st.html(textwrap.dedent(f"""
    <style>

    .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}

    .keyrorent-hero {{
        min-height: 570px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 55px 7%;
        border-radius: 18px;
        background-image:
            linear-gradient(
                90deg,
                rgba(8, 18, 38, 0.96) 0%,
                rgba(8, 18, 38, 0.82) 48%,
                rgba(8, 18, 38, 0.20) 100%
            ),
            url("data:image/png;base64,{POSTER_BASE64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        box-sizing: border-box;
    }}

    .hero-content {{
        max-width: 650px;
    }}

    .hero-title {{
        color: white;
        font-size: 52px;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 22px;
    }}

    .hero-title span {{
        color: #16B9E8;
    }}

    .hero-description {{
        color: #E2EAF5;
        font-size: 17px;
        line-height: 1.8;
        max-width: 560px;
        margin-bottom: 25px;
    }}

    .feature-tag {{
        display: inline-block;
        color: white;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.25);
        padding: 9px 14px;
        margin: 5px 5px 5px 0;
        border-radius: 20px;
        font-size: 13px;
    }}

    @media (max-width: 768px) {{
        .keyrorent-hero {{
            min-height: 520px;
            padding: 35px 22px;
            background-position: center;
        }}

        .hero-title {{
            font-size: 36px;
        }}

        .hero-description {{
            font-size: 15px;
        }}
    }}

    </style>

    <div class="keyrorent-hero">
        <div class="hero-content">

            <div class="hero-title">
                Your Journey.<br>
                Your Comfort.<br>
                <span>Our AI Support.</span>
            </div>

            <div class="hero-description">
                Experience smarter rental assistance with
                KeyroRent AI. Get instant support for your
                booking, cancellation, payments and
                rental-related questions.
            </div>

            <div>
                <span class="feature-tag">✦ AI Powered</span>
                <span class="feature-tag">✦ 24/7 Assistance</span>
                <span class="feature-tag">✦ Multilingual Support</span>
            </div>

        </div>
    </div>
    """))

    if st.button(
        "💬  Chat with KeyroRent AI",
        key="home_chat_button"
    ):
        st.session_state.page = "chat"
        st.rerun()

    st.markdown("""
    <div class="footer">
        © 2026 KeyroRent AI Assistant.
        Powered by Generative AI.
        <br><br>
        Smart Support. Better Rental Experience.
    </div>
    """, unsafe_allow_html=True)


elif st.session_state.page == "chat":

    st.html("""
    <div class="chat-header">

        <h1>🚗 KeyroRent AI Assistant</h1>

        <p>
            Your Intelligent Rental Customer Support Assistant
        </p>

        <p>
            Ask your questions in English, Telugu or Roman Telugu.
        </p>

    </div>
    """)


    # NAVIGATION BUTTONS

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "⬅ Back to Home",
            use_container_width=True,
            key="back_home_button"
        ):

            st.session_state.page = "home"

            st.rerun()


    with col2:

        if st.button(
            "🗑 Clear Chat",
            use_container_width=True,
            key="clear_chat_button"
        ):

            st.session_state.messages = []

            st.rerun()


    st.markdown("---")


    # WELCOME MESSAGE

    if not st.session_state.messages:

        with st.chat_message("assistant"):

            st.write(
                "Welcome to KeyroRent AI! 👋 "
                "How can I help you with your rental questions today?"
            )


    # DISPLAY PREVIOUS CONVERSATION

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.write(message["content"])

            if message.get("timestamp"):
                st.caption(f"🕒 {message['timestamp']}")


    # CUSTOMER INPUT

    question = st.chat_input(
        "Ask your rental question here..."
    )


    if question:

        # SAVE USER MESSAGE

        user_timestamp = datetime.now().strftime("%I:%M %p")

        st.session_state.messages.append({
            "role": "user",
            "content": question,
            "timestamp": user_timestamp
        })


        with st.chat_message("user"):

            st.write(question)


        try:

            # PREVIOUS CONVERSATION

            previous_history = st.session_state.messages[:-1]

            chat_history = [
                {
                    "role": message["role"],
                    "content": message["content"]
                }
                for message in previous_history
            ]


            # FASTAPI REQUEST

            with st.spinner("🤖 KeyroRent AI is typing..."):
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


        except requests.exceptions.RequestException as e:

            st.error(f"DEBUG - API Request Error: {repr(e)}")

            answer = (
                "Sorry, the chatbot service is currently unavailable. "
                "Please try again later."
            )

        except (KeyError, ValueError):

            answer = (
                "Sorry, something went wrong while processing your request."
            )


        # SAVE ASSISTANT RESPONSE

        assistant_timestamp = datetime.now().strftime("%I:%M %p")

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "timestamp": assistant_timestamp
        })


        with st.chat_message("assistant"):

            st.write(answer)


    # CHAT FOOTER

    st.markdown("""
    <div class="footer">
        KeyroRent AI | Intelligent Rental Support
        <br>
        Powered by Generative AI
    </div>
    """, unsafe_allow_html=True)
