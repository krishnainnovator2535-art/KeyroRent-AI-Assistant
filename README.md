
# 🚗 KeyroRent AI Assistant

An AI-powered rental customer support chatbot built using Generative AI, RAG (Retrieval-Augmented Generation), FastAPI, and Streamlit.

## 📌 Project Overview

KeyroRent AI Assistant is an intelligent customer support chatbot designed to answer rental-related questions.

It uses a Frequently Asked Questions (FAQ) knowledge base and a FAISS vector database to retrieve relevant information and generate helpful responses using Google's Gemini model.

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
- FAISS
- Sentence Transformers
- Hugging Face
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
FAISS Vector Database
   |
   v
Relevant FAQ Retrieval
   |
   v
Google Gemini
   |
   v
Final Response
