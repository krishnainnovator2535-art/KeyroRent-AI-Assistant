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

    # Double payment intent
    if any(term in q for term in [
        "charged twice", "double payment",
        "paid twice", "deducted twice"
    ]):
        terms.append(
            "duplicate charge charged twice payment deducted twice"
        )

    # Refund process intent
    elif any(term in q for term in [
        "money back", "get a refund",
        "want my money", "receive my money"
    ]):
        terms.append(
            "refund money returned reimbursement refund process"
        )

    # Refund status intent
    elif any(term in q for term in [
        "refund status", "refund delayed",
        "refund not received", "track refund"
    ]):
        terms.append(
            "refund status delayed tracking transaction reference"
        )

    # Booking cancellation intent
    if any(term in q for term in [
        "cancel my booking", "cancel a booking",
        "cancel booking", "cancellation"
    ]):
        terms.append(
            "cancel booking cancellation reservation"
        )

    # Pickup location intent
    if any(term in q for term in [
        "collect my rental",
        "collect vehicle",
        "pickup location",
        "where should i go",
        "where do i collect",
        "where can i collect"
    ]):
        terms.append(
            "pickup location confirm pickup point "
            "where to collect rental vehicle collection"
        )

    # Missing booking confirmation
    if any(term in q for term in [
        "not received a confirmation",
        "haven't received a confirmation",
        "missing confirmation",
        "no confirmation message"
    ]):
        terms.append(
            "booking confirmation not received confirmation message"
        )

    # Payment verification
    elif (
        ("payment" in q or "transaction" in q)
        and not any(term in q for term in [
            "without permission",
            "unauthorized",
            "unrecognized payment",
            "someone made a payment"
        ])
    ):
        terms.append(
            "payment verification transaction payment confirmation"
        )

    # Account deletion intent
    if any(term in q for term in [
        "close my account",
        "close my keyrorent account",
        "delete my account",
        "delete my keyrorent account",
        "deactivate my account",
        "remove my account"
    ]):
        terms.append(
            "delete account close account account deletion"
        )

    # Advance booking intent
    if any(term in q for term in [
        "before my travel date",
        "book in advance",
        "reserve in advance",
        "book early"
    ]):
        terms.append(
            "advance booking reserve vehicle beforehand "
            "book rental in advance"
        )

    # Additional charges intent
    if any(term in q for term in [
        "additional fees",
        "extra charges",
        "additional charges",
        "hidden charges"
    ]):
        terms.append(
            "hidden charges extra fees additional costs "
            "rental price"
        )

    # Rental extension intent
    if any(term in q for term in [
        "additional days",
        "extend my rental",
        "keep the rental",
        "extra days"
    ]):
        terms.append(
            "extend rental duration extension additional days"
        )

    # Minimum age intent
    if any(term in q for term in [
        "how old",
        "minimum age",
        "age requirement",
        "old must i be"
    ]):
        terms.append(
            "minimum age requirement age eligibility "
            "renting vehicle"
        )

    # Unauthorized payment intent
    if any(term in q for term in [
        "without permission",
        "unauthorized payment",
        "unauthorized rental payment",
        "unrecognized payment",
        "someone made a payment"
    ]):
        terms.append(
            "notice unauthorized rental payment "
            "unauthorized transaction account security"
        )

    # Account registration intent
    if any(term in q for term in [
        "register for a new account",
        "create a new account",
        "sign up",
        "register an account"
    ]):
        terms.append(
            "create new account account registration sign up"
        )

    # Rental comparison intent
    if any(term in q for term in [
        "compare available rental vehicles",
        "compare rental vehicles",
        "compare different rental options",
        "compare available rentals"
    ]):
        terms.append(
            "compare different rental options "
            "compare rental vehicles"
        )

    # Rental availability intent
    if any(term in q for term in [
        "available rental vehicles",
        "search for available rentals",
        "find available vehicles",
        "available rental options"
    ]):
        terms.append(
            "find available rental options search available vehicles"
        )

    # Rental photos intent
    if any(term in q for term in [
        "see pictures",
        "view pictures",
        "vehicle photos",
        "see photos",
        "pictures of a vehicle"
    ]):
        terms.append(
            "view rental photos vehicle pictures images before booking"
        )

    # Incorrect booking dates intent
    if any(term in q for term in [
        "incorrect dates",
        "wrong rental dates",
        "selected wrong dates",
        "booked incorrect dates"
    ]):
        terms.append(
            "accidentally booked wrong rental dates incorrect booking dates"
        )

    # Documents
    if "document" in q or "carry" in q:
        terms.append(
            "documents required rent vehicle"
        )

    # Mileage
    if any(term in q for term in [
        "mileage", "kilometer", "kilometre",
        "distance", "unlimited miles"
    ]):
        terms.append(
            "mileage limits distance kilometers allowance miles"
        )

    # Additional driver
    if (
        "driver" in q
        or "another person" in q
        or "someone else" in q
    ):
        terms.append(
            "another person drive rented vehicle additional driver permission"
        )

    return question + " " + " ".join(terms)

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
