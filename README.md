
# 🚗 KeyroRent AI Assistant

An AI-powered rental customer support chatbot built using Generative AI, RAG (Retrieval-Augmented Generation), FastAPI, and Streamlit.

## 📌 Project Overview

KeyroRent AI Assistant is an intelligent customer support chatbot designed to answer rental-related questions.

It uses a Frequently Asked Questions (FAQ) knowledge base and a BM25-based retrieval engine to retrieve relevant information and generate helpful responses using Google's Gemini model.

## ✨ Key Features

- AI-powered rental customer support.
- Retrieval-Augmented Generation (RAG).
- FAQ-based question answering.
- English language support.
- Telugu language support.
- Roman Telugu language support.
- Conversation history and contextual follow-up questions.
- Rental and general question classification.
- Safe responses for unsupported rental queries.
- Professional Streamlit user interface.
- FastAPI backend integration.

## 🛠️ Technologies Used

- Python
- Google Gemini
- LangChain
- FastAPI
- Streamlit
- BM25 (rank-bm25)
- Pydantic
- SlowAPI
- Pytest
- Git and GitHub
- Render
- REST API

## 🏗️ Project Architecture

```text
Customer
   |
   v
Streamlit Frontend
   |
   v
FastAPI Backend
   |
   v
Language Detection
   |
   v
Question Classification
   |
   v
Conversation Context
   |
   v
BM25 Retrieval Engine
   |
   v
Relevant FAQ Retrieval
   |
   v
Google Gemini
   |
   v
Final Response
```

## 🧪 Testing

- 22 automated tests passed using Pytest.
- Retrieval evaluation performed using 70 test cases.
- Input validation tested.
- Unsupported-question handling tested.
- API rate limiting tested locally and on the deployed backend.
- Backend health endpoint verified.

Note: Evaluation results apply to the current test dataset and do not guarantee perfect results for unseen questions.

## 🚀 Deployment

- Backend: Render
- Frontend: Streamlit Community Cloud

### 🌐 Live Demo & API

- **Live Application:** https://keyrorent-ai-assistant-ewaxixsaymirxeatsimid6.streamlit.app/
- **Backend API:** https://keyrorent-ai-assistant.onrender.com
- **Backend Health Check:** https://keyrorent-ai-assistant.onrender.com/health

Backend health endpoint:

https://keyrorent-ai-assistant.onrender.com/

## ⚙️ Run Locally

Clone the repository:

```bash
git clone https://github.com/krishnainnovator2535-art/KeyroRent-AI-Assistant.git
cd KeyroRent-AI-Assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your Gemini API key using the GEMINI_API_KEY environment variable.

Start the backend:

```bash
uvicorn backend:app --reload
```

Start the frontend in another terminal:

```bash
streamlit run streamlit_app.py
```

## 🔐 Security

- Input validation using Pydantic.
- API rate limiting using SlowAPI.
- API keys managed through environment variables and deployment secrets.
- Graceful handling of Gemini quota and service errors.

## ⚠️ Project Limitations

- Uses sample FAQ data for demonstration.
- Does not access real customer accounts or booking databases.
- Does not perform actual bookings, cancellations, payments, or refunds.
- Production use requires verified rental policies and secure backend integrations.

## 👨‍💻 Author

**Krishna**

Generative AI Enthusiast | B.Tech ECE Graduate

[GitHub Profile](https://github.com/krishnainnovator2535-art)
