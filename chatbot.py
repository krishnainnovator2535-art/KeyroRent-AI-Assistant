import re

from language import (
    detect_language,
    improved_rewrite_query,
    contextualize_question,
    convert_to_telugu,
    convert_to_roman_telugu
)

from classifier import classify_question, old_classify_question


# KEYWORD RELEVANCE VALIDATION

STOP_WORDS = {
    "does", "do", "did", "is", "are", "was", "were",
    "can", "could", "would", "should",
    "what", "how", "when", "where", "which",
    "the", "a", "an", "to", "for", "of", "in",
    "on", "my", "me", "i", "we", "you",
    "and", "or", "be", "it",
    "keyrorent", "provide", "get", "have",
    "please", "tell", "about", "want"
}

SYNONYMS = {
    "money": {"refund", "reimbursement"},
    "back": {"refund", "returned"},
    "collect": {"pickup"},
    "pick": {"pickup"},
    "car": {"vehicle"},
    "automobile": {"vehicle"},
    "vehicle": {"car"},
    "cancel": {"cancellation"},
    "cancellation": {"cancel"},
    "reservation": {"booking"},
    "booking": {"reservation"},
    "documents": {"document"},
    "document": {"documents"},
    "late": {"delay", "delayed"},
    "delay": {"late"},
    "drivers": {"driver"},
    "driver": {"drivers"}
}


def important_tokens(text):

    text = text.lower()

    # Normalize equivalent extra-driver phrases
    phrase_patterns = {
        r"\bextra driver\b": "extradriver",
        r"\badditional driver\b": "extradriver",
        r"\banother person (?:to )?drive\b": "extradriver",
        r"\bsomeone else (?:to )?drive\b": "extradriver"
    }

    for pattern, replacement in phrase_patterns.items():
        text = re.sub(pattern, replacement, text)

    words = re.findall(r"\b\w+\b", text)

    ignored_words = STOP_WORDS | {
        "rental", "rented", "vehicle", "vehicles", "rent"
    }

    return {
        word for word in words
        if word not in ignored_words
    }


def expand_important_tokens(text):

    tokens = important_tokens(text)

    expanded = set(tokens)

    for token in tokens:
        expanded.update(
            SYNONYMS.get(token, set())
        )

    return expanded


def calculate_keyword_overlap(query, document_question):

    query_tokens = expand_important_tokens(query)

    document_tokens = expand_important_tokens(
        document_question
    )

    if not query_tokens:
        return 0.0

    common_tokens = query_tokens.intersection(
        document_tokens
    )

    return len(common_tokens) / len(query_tokens)


def select_relevant_documents(query, results, max_docs=10):

    relevant_docs = []

    for doc, score in results:

        faq_question = doc.metadata.get("question", "")

        overlap = calculate_keyword_overlap(
            query,
            faq_question
        )

        relevant_docs.append(
            (doc, float(score), overlap)
        )

    relevant_docs.sort(
        key=lambda item: (item[1], item[2]),
        reverse=True
    )

    return [
        doc
        for doc, score, overlap
        in relevant_docs[:max_docs]
    ]


def build_context_aware_search_question(
    contextual_question,
    chat_history
):

    question = contextual_question.lower()

    previous_messages = " ".join(
        message["content"].lower()
        for message in chat_history
        if message["role"] == "user"
    )

    cancellation_patterns = [
        "cancel",
        "cancellation",
        "booking cancellation"
    ]

    has_cancellation_context = any(
        pattern in previous_messages
        for pattern in cancellation_patterns
    )

    if not has_cancellation_context:
        return contextual_question

    time_patterns = [
        "how many days",
        "how long",
        "processing time",
        "how long does it take",
        "when will i receive"
    ]

    if any(pattern in question for pattern in time_patterns):

        return (
            "How long does refund processing take "
            "after cancelling my booking?"
        )

    contact_patterns = [
        "who should i contact",
        "whom should i contact",
        "who can i contact",
        "contact regarding the refund"
    ]

    if any(pattern in question for pattern in contact_patterns):

        return (
            "Who should I contact regarding my "
            "refund after booking cancellation?"
        )

    refund_patterns = [
        "money back",
        "refund",
        "get my money",
        "receive my money"
    ]

    if any(pattern in question for pattern in refund_patterns):

        return (
            "Will I get a refund after cancelling my booking? "
            "What determines refund eligibility?"
        )

    return contextual_question


# SMART RESPONSES


def get_smart_response(question, llm=None, chat_history=None):

    if chat_history is None:
        chat_history = []

    category = classify_question(question)

    if category == "rental":
        category = old_classify_question(question)

    language = detect_language(question)

    responses = {
        "greeting": (
            "Hello! Welcome to KeyroRent AI Assistant. "
            "How can I help you with your rental-related queries today?"
        ),

        "gratitude": (
            "You're welcome! Happy to help you. "
            "Let me know if you need anything else."
        ),

        "acknowledgement": (
            "Sure! I'm here if you need any further assistance."
        ),

        "cancellation": (
            "Sure! Do you want to cancel your rental booking? "
            "I can guide you through the cancellation process."
        ),

        "refund": (
            "I can help you with refund-related questions. "
            "Are you asking about refund eligibility, "
            "processing time, or refund status?"
        )
    }

    if category not in responses:
        return None

    answer = responses[category]

    if language == "Telugu":
        answer = convert_to_telugu(answer, llm)

    elif language == "Roman Telugu":
        answer = convert_to_roman_telugu(answer, llm)

    chat_history.append({
        "role": "user",
        "content": question
    })

    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    return answer


# SINGLE QUESTION CHATBOT


def keyrorent_single_question_with_memory(
    question,
    chat_history=None,
    llm=None,
    bm25_index=None,
    rag_prompt=None,
    conversation_context_prompt=None
):

    if chat_history is None:
        chat_history = []

    if bm25_index is None:
        raise ValueError("BM25 index is not initialized.")

    language = detect_language(question)

    contextual_question = contextualize_question(
        question,
        chat_history,
        llm,
        conversation_context_prompt
    )

    print("Contextualized Question:", contextual_question)

    rewritten_question = improved_rewrite_query(
        contextual_question,
        llm
    )

    print("\nRewritten English Question:", rewritten_question)

    search_question = build_context_aware_search_question(
        rewritten_question,
        chat_history
    )

    print("\nFinal Search Question:", search_question)

    category = classify_question(search_question)

    if category == "general":

        general_answer = (
            "I'm here to help with KeyroRent rental services. "
            "I can assist you with bookings, cancellations, payments, "
            "refunds, and rental-related questions."
        )

        if language == "Telugu":
            general_answer = convert_to_telugu(general_answer, llm)

        elif language == "Roman Telugu":
            general_answer = convert_to_roman_telugu(general_answer, llm)

        chat_history.append({
            "role": "user",
            "content": question
        })

        chat_history.append({
            "role": "assistant",
            "content": general_answer
        })

        return general_answer

    # BM25 RETRIEVAL

    results = bm25_index.similarity_search_with_score(
        search_question,
        k=10
    )

    relevant_docs = select_relevant_documents(
        search_question,
        results,
        max_docs=3
    )

    if not relevant_docs:

        unavailable_message = (
            "I'm sorry, I couldn't find verified information "
            "about this topic. Please contact KeyroRent customer support."
        )

        if language == "Telugu":
            unavailable_message = convert_to_telugu(unavailable_message, llm)

        elif language == "Roman Telugu":
            unavailable_message = convert_to_roman_telugu(unavailable_message, llm)

        chat_history.append({
            "role": "user",
            "content": question
        })

        chat_history.append({
            "role": "assistant",
            "content": unavailable_message
        })

        return unavailable_message

    if rag_prompt is None:
        raise ValueError("RAG prompt is not configured.")

    context = "\n\n".join(
        doc.page_content for doc in relevant_docs
    )

    messages = rag_prompt.format_messages(
        context=context,
        question=search_question,
        language=language
    )

    response = llm.invoke(messages)

    answer = response.content

    if isinstance(answer, list):
        answer = " ".join(
            item.get("text", "")
            if isinstance(item, dict)
            else str(item)
            for item in answer
        )

    answer = str(answer).strip()

    if language == "Telugu":
        answer = convert_to_telugu(answer, llm)

    elif language == "Roman Telugu":
        answer = convert_to_roman_telugu(answer, llm)

    chat_history.append({
        "role": "user",
        "content": question
    })

    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    return answer


# MULTI-QUESTION CHATBOT


def keyrorent_chatbot_with_memory(
    question,
    chat_history=None,
    llm=None,
    bm25_index=None,
    rag_prompt=None,
    conversation_context_prompt=None
):

    if chat_history is None:
        chat_history = []

    questions = re.split(r'\?\s*|\n+', question.strip())

    questions = [
        re.sub(r'^\s*\d+[\).:-]\s*', '', q).strip(" \t\r\n.!?")
        for q in questions
    ]

    questions = [q for q in questions if q]

    if len(questions) == 1:

        smart_answer = get_smart_response(
            questions[0],
            llm,
            chat_history
        )

        if smart_answer is not None:
            return smart_answer

        return keyrorent_single_question_with_memory(
            questions[0],
            chat_history,
            llm,
            bm25_index,
            rag_prompt,
            conversation_context_prompt
        )

    answers = []

    updated_history = chat_history

    for index, current_question in enumerate(questions, start=1):

        smart_answer = get_smart_response(
            current_question,
            llm,
            updated_history
        )

        if smart_answer is not None:
            answer = smart_answer

        else:
            answer = keyrorent_single_question_with_memory(
                current_question,
                updated_history,
                llm,
                bm25_index,
                rag_prompt,
                conversation_context_prompt
            )

        answers.append(f"{index}. {answer}")


    return "\n\n".join(answers)
