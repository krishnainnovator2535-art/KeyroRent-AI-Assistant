import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document


# PROJECT PATHS

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FAQ_PATH = DATA_DIR / "faqs.json"


# FAQ LOADING

def load_faqs():

    with open(FAQ_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# TEXT TOKENIZATION

def tokenize(text):

    return re.findall(r"\b\w+\b", text.lower())


# QUERY EXPANSION

def expand_rental_query(question):

    q = question.lower()
    terms = []

    if "payment" in q or "pay" in q:
        terms.append("payment methods accepted transaction")

    if any(term in q for term in ["collect", "pickup", "pick up", "pick-up"]):
        terms.append("pickup location pick up collect vehicle confirm where to get rental car vehicle")

    if "document" in q or "carry" in q:
        terms.append("documents required rent vehicle")

    if "cancel" in q or "cancellation" in q:
        terms.append("cancel booking cancellation confirmed reservation")

    if "refund" in q or "money back" in q:
        terms.append("refund status money returned reimbursement")

    if "confirmed" in q or "confirmation" in q:
        terms.append("booking confirmed reservation confirmation status")

    if "hidden charges" in q or "extra charges" in q:
        terms.append("hidden fees additional costs pricing")

    # Mileage query expansion
    if any(term in q for term in [
        "mileage", "kilometer", "kilometre",
        "distance", "unlimited miles"
    ]):
        terms.append(
            "mileage limits distance kilometers allowance "
            "kilometres miles permitted travel distance"
        )

    # Extra driver query expansion
    if (
        "driver" in q
        or "another person" in q
        or "someone else" in q
    ):
        terms.append(
            "another person drive rented vehicle additional driver permission"
        )

    return question + " " + " ".join(terms)


# BM25 INDEX

class BM25Index:

    def __init__(self, faqs):

        self.faqs = faqs

        self.corpus = [
            tokenize(faq["question"])
            for faq in faqs
        ]

        self.model = BM25Okapi(self.corpus)

    def similarity_search_with_score(self, question, k=5):

        expanded_question = expand_rental_query(question)

        tokens = tokenize(expanded_question)

        scores = self.model.get_scores(tokens)

        ranked_indices = scores.argsort()[::-1][:k]

        results = []

        for index in ranked_indices:

            faq = self.faqs[index]

            document = Document(
                page_content=(
                    f"Question: {faq['question']}\n"
                    f"Answer: {faq['answer']}"
                ),
                metadata={
                    "question": faq["question"]
                }
            )

            results.append(
                (document, float(scores[index]))
            )

        return results


# BM25 INITIALIZATION

def load_bm25_index(faqs):

    return BM25Index(faqs)


# FAQ RETRIEVAL

def retrieve_faqs(question, bm25_index, rewrite_query=None, k=5):

    rewritten_question = (
        rewrite_query(question)
        if rewrite_query
        else question
    )

    return bm25_index.similarity_search_with_score(
        rewritten_question,
        k=k
    )
