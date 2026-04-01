from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

# NLP + services
from nlp.sentiment import analyze_sentiment
from nlp.language import detect_language
from services.router import route_query
from services.faq import get_faq_answer

import os
from dotenv import load_dotenv

load_dotenv()

# Gemini config
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("API key not found. Check your .env file.")

app = FastAPI()

# 📦 Dummy Order DB
orders = {
    "123": "Shipped",
    "456": "Processing",
    "789": "Delivered"
}

# 🌍 Multilingual Order Replies
order_replies = {
    "en": "📦 Your order is shipped and will arrive soon.",
    "hi": "📦 आपका ऑर्डर भेज दिया गया है और जल्द ही पहुँच जाएगा।",
    "bn": "📦 আপনার অর্ডার পাঠানো হয়েছে এবং শীঘ্রই পৌঁছাবে।",
    "or": "📦 ଆପଣଙ୍କ ଅର୍ଡର ପଠାଯାଇଛି ଏବଂ ଶୀଘ୍ର ପହଞ୍ଚିବ।",
    "te": "📦 మీ ఆర్డర్ పంపించబడింది మరియు త్వరలో చేరుతుంది.",
    "ta": "📦 உங்கள் ஆர்டர் அனுப்பப்பட்டுள்ளது மற்றும் விரைவில் வரும்.",
    "as": "📦 আপোনাৰ অৰ্ডাৰ পঠোৱা হৈছে আৰু শীঘ্ৰে আহিব।",
    "ur": "📦 آپ کا آرڈر بھیج دیا گیا ہے اور جلد پہنچ جائے گا۔",
    "pa": "📦 ਤੁਹਾਡਾ ਆਰਡਰ ਭੇਜ ਦਿੱਤਾ ਗਿਆ ਹੈ ਅਤੇ ਜਲਦੀ ਪਹੁੰਚੇਗਾ।",
    "ml": "📦 നിങ്ങളുടെ ഓർഡർ അയച്ചുകഴിഞ്ഞു, ഉടൻ എത്തും."
}

# 🌍 Multilingual Order Keywords
order_keywords = [
    "order", "track", "status",
    "ऑर्डर", "आदेश",
    "অর্ডার",
    "ଅର୍ଡର",
    "ఆర్డర్",
    "ஆர்டர்",
    "অৰ্ডাৰ",
    "آرڈر",
    "ਆਰਡਰ",
    "ഓർഡർ"
]

@app.get("/")
def home():
    return {"message": "Server running successfully"}


@app.post("/webhook")
async def webhook(request: Request):
    form_data = await request.form()

    message = form_data.get("Body", "")
    print("\nUser:", message)

    # 🌍 Language detection
    language = detect_language(message)
    print("Language:", language)

    # 😊 Sentiment
    sentiment, score = analyze_sentiment(message)
    print("Sentiment:", sentiment, score)

    # 🔀 Routing
    route = route_query(sentiment, score, message)
    print("Route:", route)

    msg = message.lower()

    # 📚 FAQ
    faq_reply = get_faq_answer(msg, language)

    # 🎯 FINAL DECISION LOGIC
    if faq_reply:
        reply = faq_reply

    elif any(word in msg for word in order_keywords):
        reply = order_replies.get(language, order_replies["en"])

    elif route == "HUMAN":
        reply = "⚠️ You seem upset. Connecting to a human agent..."

    else:
        response = model.generate_content(message)
        reply = response.text

    # Clean
    reply = reply.replace("*", "").replace("#", "")
    reply = reply.strip()
    reply = reply[:1500]

    print("Bot:", reply)

    # Twilio response
    twilio_response = MessagingResponse()
    twilio_response.message(reply)

    return PlainTextResponse(
        content=str(twilio_response),
        media_type="application/xml"
    )