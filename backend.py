
import os
import sys
from pathlib import Path
from typing import List, Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from knowledge_base import (
    load_faqs,
    load_embedding_model,
    load_vector_store
)

from chatbot import keyrorent_chatbot_with_memory


# PROJECT CONFIGURATION

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


# GEMINI CONFIGURATION

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing!")


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GEMINI_API_KEY
)


# KNOWLEDGE BASE INITIALIZATION

faqs = load_faqs()

embedding_model = load_embedding_model()

vector_store = load_vector_store(embedding_model)


# CHATBOT CONFIGURATION

RELEVANCE_THRESHOLD = 20.0

app = FastAPI(
    title="KeyroRent AI Assistant API",
    description="AI-powered rental customer support API",
    version="1.0.0"
)


print("KeyroRent backend initialized successfully!")
print("Total FAQs:", len(faqs))


# API REQUEST AND RESPONSE MODELS

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Customer rental support question"
    )
    chat_history: List[ChatMessage] = Field(
        default_factory=list
    )


class ChatResponse(BaseModel):
    question: str
    answer: str


print("API models added successfully!")


# HOME ENDPOINT

@app.get("/")
def home():
    return {
        "message": "Welcome to KeyroRent AI Assistant API",
        "status": "Running"
    }


# CHAT ENDPOINT

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in request.chat_history
    ]

    answer = keyrorent_chatbot_with_memory(
        question=request.question,
        chat_history=history,
        llm=llm,
        vector_store=vector_store,
        rag_prompt=rag_prompt,
        conversation_context_prompt=conversation_context_prompt,
        relevance_threshold=RELEVANCE_THRESHOLD
    )

    return ChatResponse(
        question=request.question,
        answer=answer
    )


print("FastAPI endpoints added successfully!")

# PROMPT CONFIGURATION

from langchain_core.prompts import ChatPromptTemplate


rag_prompt = ChatPromptTemplate.from_messages([
    (
        "human",
        """
You are KeyroRent AI, a professional rental customer support assistant.

STRICT RULES:
1. Answer only KeyroRent rental-related questions.
2. Use only the provided knowledge base.
3. Never invent company policies or information.
4. If information is unavailable, clearly say so.
5. Keep answers short, clear and professional.
6. Do not add unrelated information.

MANDATORY LANGUAGE RULES:

The detected customer language is: {language}

If language is English:
Answer entirely in English.

If language is Telugu:
Answer entirely in Telugu script.

If language is Roman Telugu:
Answer entirely in Roman Telugu using English letters.
Do not use Telugu script.
Do not answer in English.

Knowledge Base:
{context}

Customer Question:
{question}

Answer:
"""
    )
])


conversation_context_prompt = ChatPromptTemplate.from_messages([
    (
        "human",
        """
You are a conversation context assistant for KeyroRent.

Your task is to understand the customer's latest question
using the previous conversation.

Rules:
1. Read the previous conversation carefully.
2. Understand what the customer is referring to.
3. Convert the latest question into a complete standalone English question.
4. Preserve the customer's original meaning.
5. Do not answer the question.
6. Do not invent missing details.
7. If the question is already complete, preserve its meaning.
8. Return only the standalone English question.

Previous Conversation:
{chat_history}

Latest Customer Question:
{question}

Standalone English Question:
"""
    )
])


print("Prompt configurations added successfully!")
