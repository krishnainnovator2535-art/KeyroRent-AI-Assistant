
def old_classify_question(question):

    question = question.lower().strip()
    question = question.strip("!?., ")

    greetings = [
        "hi", "hello", "hey",
        "good morning", "good afternoon",
        "good evening", "hii", "helo"
    ]

    if question in greetings:
        return "greeting"

    gratitude = [
        "thank you", "thanks",
        "thankyou", "thx"
    ]

    if question in gratitude:
        return "gratitude"

    acknowledgements = [
        "okay", "ok", "sure",
        "alright", "fine"
    ]

    if question in acknowledgements:
        return "acknowledgement"

    cancellation = [
        "cancel", "cancellation",
        "booking cancel", "cancel booking"
    ]

    if question in cancellation:
        return "cancellation"

    refunds = [
        "refund", "refund status",
        "refund details"
    ]

    if question in refunds:
        return "refund"

    rental_keywords = [
        "rental", "rent", "booking", "reservation",
        "property", "payment", "refund", "cancellation",
        "cancel", "customer support", "keyrorent",
        "account", "login", "password", "vehicle",
        "driver", "additional driver", "extra driver",
        "another person drive", "roadside assistance",
        "fuel", "mileage",
        "insurance", "rental duration", "rental period",
        "checkout", "transaction", "return",
        "phone number", "email address", "profile",
        "register", "registration", "verification",
        "account details", "update my"
    ]

    roman_telugu_keywords = [
        "naa booking", "booking cancel",
        "booking ni", "nenu booking",
        "ela cancel", "cancel cheyyali",
        "refund vastunda", "dabbu vastunda",
        "password marchipoyanu", "reset cheyyali",
        "rent ki", "rental ki",
        "phone number marchali",
        "email marchali",
        "account update cheyyali"
    ]

    telugu_keywords = [
        "బుకింగ్", "రద్దు", "ఫోన్ నంబర్",
        "పాస్‌వర్డ్", "రీసెట్", "రెంటల్",
        "ఇన్సూరెన్స్", "వాహనం", "ఖాతా",
        "ఈమెయిల్", "నమోదు", "ప్రొఫైల్",
        "రిఫండ్", "చెల్లింపు"
    ]

    for keyword in (
        rental_keywords
        + roman_telugu_keywords
        + telugu_keywords
    ):
        if keyword in question:
            return "rental"

    return "general"


def classify_question(question):

    text = question.lower().strip()

    refund_patterns = [
        "money back",
        "get my money back",
        "receive my money",
        "get a refund",
        "refund status",
        "refund processing",
        "refund eligibility",
        "refund policy",
        "processing time",
        "refund"
    ]

    for pattern in refund_patterns:
        if pattern in text:
            return "rental"

    return old_classify_question(question)
