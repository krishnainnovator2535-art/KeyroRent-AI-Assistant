
from knowledge_base import load_faqs, load_bm25_index


def test_faq_count():
    faqs = load_faqs()
    assert len(faqs) == 96


def test_cancellation_retrieval():
    faqs = load_faqs()
    bm25_index = load_bm25_index(faqs)

    results = bm25_index.similarity_search_with_score(
        "How can I cancel my booking?",
        k=5
    )

    retrieved_questions = [
        doc.metadata["question"]
        for doc, score in results
    ]

    assert "How can I cancel a confirmed booking?" in retrieved_questions


import pytest


@pytest.mark.parametrize("query, expected_question", [
    (
        "What payment methods can I use?",
        "What payment methods can I use?"
    ),
    (
        "How can I check my refund status?",
        "How can I check my refund status?"
    ),
    (
        "How can I confirm the pickup location for my rental?",
        "How can I confirm the pickup location for my rental?"
    ),
    (
        "What documents are required to rent a vehicle?",
        "What documents are required to rent a vehicle?"
    ),
])
def test_category_retrieval(query, expected_question):
    faqs = load_faqs()
    bm25_index = load_bm25_index(faqs)

    results = bm25_index.similarity_search_with_score(
        query,
        k=5
    )

    retrieved_questions = [
        doc.metadata["question"]
        for doc, score in results
    ]

    assert expected_question in retrieved_questions


from classifier import classify_question


def test_rental_question_classification():
    assert classify_question(
        "How can I cancel my booking?"
    ) == "rental"


def test_general_question_classification():
    assert classify_question(
        "What is the capital of India?"
    ) == "general"


def test_unknown_rental_topic_classification():
    assert classify_question(
        "Is roadside assistance available?"
    ) == "rental"


def test_insurance_question_classification():
    assert classify_question(
        "Can I get insurance for my rental?"
    ) == "rental"


from language import detect_language


def test_english_language_detection():
    assert detect_language(
        "How can I cancel my booking?"
    ) == "English"


def test_roman_telugu_detection():
    assert detect_language(
        "Naa booking ni ela cancel cheyyali?"
    ) == "Roman Telugu"


def test_telugu_script_detection():
    assert detect_language(
        "నా బుకింగ్ ఎలా క్యాన్సిల్ చేయాలి?"
    ) == "Telugu"


from unittest.mock import MagicMock, patch
import chatbot


@pytest.mark.parametrize("question", [
    "Is roadside assistance available?",
    "Is free fuel included?",
    "Can I get a replacement vehicle during a breakdown?"
])
def test_unsupported_questions_do_not_call_gemini(question):

    faqs = load_faqs()
    bm25_index = load_bm25_index(faqs)

    fake_llm = MagicMock()
    chat_history = []

    with patch.object(
        chatbot,
        "contextualize_question",
        return_value=question
    ), patch.object(
        chatbot,
        "improved_rewrite_query",
        return_value=question
    ):

        answer = chatbot.keyrorent_single_question_with_memory(
            question=question,
            chat_history=chat_history,
            llm=fake_llm,
            bm25_index=bm25_index,
            rag_prompt=MagicMock(),
            conversation_context_prompt=None
        )

    assert not fake_llm.invoke.called
    assert "couldn't find verified information" in answer
    assert len(chat_history) == 2


@pytest.mark.parametrize("question", [
    "Does KeyroRent provide insurance?",
    "How can I cancel my booking?",
    "What payment methods are accepted?"
])
def test_supported_questions_call_gemini(question):

    faqs = load_faqs()
    bm25_index = load_bm25_index(faqs)

    fake_llm = MagicMock()
    fake_llm.invoke.return_value.content = (
        "This is a simulated answer for testing."
    )

    fake_prompt = MagicMock()
    fake_prompt.format_messages.return_value = ["Test message"]

    with patch.object(
        chatbot,
        "contextualize_question",
        return_value=question
    ), patch.object(
        chatbot,
        "improved_rewrite_query",
        return_value=question
    ):

        answer = chatbot.keyrorent_single_question_with_memory(
            question=question,
            chat_history=[],
            llm=fake_llm,
            bm25_index=bm25_index,
            rag_prompt=fake_prompt,
            conversation_context_prompt=None
        )

    assert fake_llm.invoke.called
    assert answer == "This is a simulated answer for testing."

    context = fake_prompt.format_messages.call_args.kwargs["context"]
    assert len(context) > 0


def test_unauthorized_payment_retrieval_rank_one():

    faqs = load_faqs()
    bm25_index = load_bm25_index(faqs)

    query = (
        "Someone made a payment using my account "
        "without permission."
    )

    expected_question = (
        "What should I do if I notice an unauthorized rental payment?"
    )

    results = bm25_index.similarity_search_with_score(
        query,
        k=5
    )

    retrieved_questions = [
        doc.metadata["question"]
        for doc, score in results
    ]

    assert retrieved_questions[0] == expected_question


def test_rental_comparison_retrieval_rank_one():

    faqs = load_faqs()
    bm25_index = load_bm25_index(faqs)

    query = "How do I compare available rental vehicles?"

    expected = "How can I compare different rental options?"

    results = bm25_index.similarity_search_with_score(
        query,
        k=5
    )

    retrieved = [
        doc.metadata["question"]
        for doc, score in results
    ]

    assert retrieved[0] == expected


def test_rental_availability_retrieval_rank_one():

    faqs = load_faqs()
    bm25_index = load_bm25_index(faqs)

    query = "Where can I search for available rental vehicles?"

    expected = "How can I find available rental options?"

    results = bm25_index.similarity_search_with_score(
        query,
        k=5
    )

    retrieved = [
        doc.metadata["question"]
        for doc, score in results
    ]

    assert retrieved[0] == expected
