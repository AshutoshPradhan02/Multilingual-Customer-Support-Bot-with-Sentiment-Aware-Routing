def route_query(sentiment, score, message):
    msg = message.lower()

    # ✅ SAFE INTENT KEYWORDS (multilingual)
    safe_words = [
        # English
        "order", "status", "track", "where",

        # Hindi
        "ऑर्डर", "ऑडर", "कहाँ", "क्या",

        # Bengali
        "অর্ডার",

        # Odia
        "ଅର୍ଡର",

        # Telugu
        "ఆర్డర్",

        # Tamil
        "ஆர்டர்",

        # Malayalam
        "ഓർഡർ"
    ]

    # 👉 If it's a normal query → NEVER escalate
    if any(word in msg for word in safe_words):
        return "BOT"

    # 🚨 Strong escalation keywords
    urgent_words = [
        "refund", "cancel", "worst", "angry", "complaint",
        "खराब", "बेकार", "गलत", "रिफंड दो"
    ]

    if any(word in msg for word in urgent_words):
        return "HUMAN"

    # 🚨 Only very strong negative
    if sentiment == "NEGATIVE" and score > 0.95:
        return "HUMAN"

    return "BOT"