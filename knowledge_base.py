
import json
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# PROJECT PATHS

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

FAQ_PATH = DATA_DIR / "faqs.json"

FAISS_PATH = DATA_DIR / "faiss_index"


# EMBEDDING MODEL

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def load_faqs():

    with open(FAQ_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_embedding_model():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )


def load_vector_store(embedding_model):

    return FAISS.load_local(
        str(FAISS_PATH),
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )


def retrieve_faqs(question, vector_store, rewrite_query, k=3):

    rewritten_question = rewrite_query(question)

    results = vector_store.similarity_search_with_score(
        rewritten_question,
        k=k
    )

    return results
