
def extract_response_text(response):

    content = response.content

    if isinstance(content, str):
        return content.strip()

    elif isinstance(content, list):
        return "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict)
            and item.get("type") == "text"
        ).strip()

    return str(content).strip()


def old_detect_language(question):

    telugu_range = any(
        '\u0C00' <= char <= '\u0C7F'
        for char in question
    )

    if telugu_range:
        return "Telugu"

    roman_telugu_keywords = [
        "naa", "nenu", "naaku", "naku",
        "ela", "cheyyali", "marchali",
        "vastunda", "vastundi", "avuthunda",
        "avuthundi", "chesukovali",
        "chesthe", "chesina", "eppudu",
        "ekkada", "enduku", "em avuthundi",
        "untunda", "untundi", "cheppandi",
        "ivvandi", "kavali", "ledu"
    ]

    words = question.lower().split()

    matches = sum(
        1 for word in roman_telugu_keywords
        if word in words
    )

    if matches >= 1:
        return "Roman Telugu"

    return "English"


def detect_language(question):

    text = question.lower().strip()

    roman_telugu_patterns = [
        "naa dabbulu",
        "tirigi vastaya",
        "enni rojullo",
        "rojullo vastayi",
        "evarini contact",
        "contact cheyyali",
        "ela cheyyali",
        "cheyyali",
        "vastaya",
        "vastundi",
        "dabbulu",
        "tirigi",
        "evarini",
        "rojullo"
    ]

    for pattern in roman_telugu_patterns:
        if pattern in text:
            return "Roman Telugu"

    return old_detect_language(question)


def rewrite_query(question):
    return question


def improved_rewrite_query(question, llm):

    rewrite_prompt = f"""
    Translate the following customer question into clear,
    natural English.

    Rules:
    1. If the question is in Telugu script, translate it into English.
    2. If the question is in Roman Telugu, translate it into English.
    3. If the question is already in English, rewrite it clearly.
    4. Preserve the original meaning.
    5. Return ONLY the English question.
    6. Do not answer the question.

    Customer Question: {question}

    English Question:
    """

    response = llm.invoke(rewrite_prompt)

    return extract_response_text(response)


def contextualize_question(
    question,
    chat_history,
    llm,
    conversation_context_prompt
):

    if not chat_history:
        return rewrite_query(question)

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in chat_history
    )

    messages = conversation_context_prompt.format_messages(
        chat_history=history_text,
        question=question
    )

    response = llm.invoke(messages)

    return extract_response_text(response)


def convert_to_telugu(answer, llm):

    conversion_prompt = f"""
    You are an expert Telugu translator.

    Translate the answer into natural Telugu language.

    STRICT RULES:
    1. Use Telugu Unicode script only.
    2. Never use Hindi or Devanagari characters.
    3. Do not mix English, Hindi or other scripts.
    4. Preserve the original meaning exactly.
    5. Return only the translated Telugu text.

    Answer:
    {answer}
    """

    response = llm.invoke(conversion_prompt)
    converted = extract_response_text(response).strip()

    # Check for Devanagari characters
    has_devanagari = any(
        '\u0900' <= char <= '\u097F'
        for char in converted
    )

    # Retry if Hindi/Devanagari characters appear
    if has_devanagari:
        retry_prompt = f"""
        Translate this answer into pure Telugu language
        using Telugu Unicode script only.

        Do not use Devanagari or Hindi characters.

        Answer:
        {answer}

        Return only Telugu translation.
        """

        retry_response = llm.invoke(retry_prompt)
        converted = extract_response_text(retry_response).strip()

    return converted


def convert_to_roman_telugu(answer, llm):

    conversion_prompt = f"""
    Convert this answer into natural conversational Roman Telugu.

    Rules:
    1. Use English alphabets only.
    2. Write Telugu language using English letters.
    3. Do not use Telugu script.
    4. Translate English sentences into natural Telugu.
    5. Preserve the original meaning.
    6. Do not add new information.
    7. Return only the converted answer.

    Answer:
    {answer}
    """

    response = llm.invoke(conversion_prompt)

    converted = extract_response_text(response)

    has_telugu_script = any(
        '\u0C00' <= char <= '\u0C7F'
        for char in converted
    )

    if has_telugu_script:

        retry_prompt = f"""
        Rewrite the following answer entirely in Roman Telugu.

        IMPORTANT:
        - Use English alphabets only.
        - Do not use any Telugu script.
        - Translate all Telugu-script words into Roman Telugu.
        - Preserve the original meaning.
        - Return only the corrected answer.

        Answer:
        {converted}
        """

        retry_response = llm.invoke(retry_prompt)

        converted = extract_response_text(retry_response)

    return converted
