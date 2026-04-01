# Multilingual-Customer-Support-Bot-with-Sentiment-Aware-Routing
Multilingual Customer Support Bot with Sentiment-Aware Routing

# 🌍 Multilingual Customer Support Bot with Sentiment-Aware Routing

---

## 📌 Project Summary

This project is an AI-powered **Multilingual Customer Support Bot** designed to handle user queries across multiple languages while intelligently routing conversations based on sentiment.

The system integrates:

* 🌍 Multilingual NLP (10 languages)
* 😊 Sentiment analysis
* 🔀 Smart routing (Bot vs Human)
* 📚 FAQ retrieval system
* 📦 Order tracking system
* 🤖 AI fallback using Gemini

---

## 🎯 Problem Statement

E-commerce platforms struggle to:

* Handle queries across multiple languages
* Detect frustrated/angry users
* Scale customer support efficiently

👉 This system solves:

* Language barriers
* Delayed response times
* Poor customer experience

---

## 🚀 Key Features

✔ Supports 10 languages (English, Hindi, Bengali, Odia, Telugu, Tamil, Assamese, Urdu, Punjabi, Malayalam)
✔ Detects sentiment of user queries
✔ Routes angry users to human agents
✔ Provides instant FAQ responses
✔ Handles order tracking queries
✔ Uses AI fallback for unknown queries
✔ REST API for frontend integration
✔ WhatsApp integration using Twilio

---

## 🧠 System Architecture

User (WhatsApp / Frontend)
↓
FastAPI Backend
↓
Language Detection
↓
Sentiment Analysis
↓
Decision Engine:
→ FAQ System
→ Order Tracking
→ Human Escalation
→ Gemini AI (fallback)

---

## ⚙️ Tech Stack

* Python (FastAPI)
* HuggingFace Transformers
* Google Gemini API
* Twilio WhatsApp API
* Langdetect
* REST API architecture

---

## 📁 Project Structure

AI_SYSTEM/
│── main.py                 → Main backend API (entry point)
│── requirements.txt       → Dependencies list
│── README.md              → Documentation
│── .gitignore             → Ignored files
│── .env.example           → API key template

│── nlp/
│     ├── sentiment.py     → Sentiment analysis module
│     ├── language.py      → Language detection module

│── services/
│     ├── router.py        → Routing logic (Bot vs Human)
│     ├── faq.py           → FAQ system (multilingual)

---

## 📂 File-by-File Explanation

### 🔹 main.py

Core backend file:

* Handles API requests
* Integrates all modules
* Implements decision logic
* Connects to Gemini API
* Sends responses to frontend/WhatsApp

---

### 🔹 nlp/sentiment.py

* Uses HuggingFace transformer
* Detects sentiment (POSITIVE / NEGATIVE)
* Helps in escalation logic

---

### 🔹 nlp/language.py

* Detects input language
* Supports fallback to English
* Ensures multilingual compatibility

---

### 🔹 services/router.py

* Decides:

  * BOT → normal response
  * HUMAN → escalation
* Uses:

  * sentiment score
  * keyword override logic

---

### 🔹 services/faq.py

* Handles predefined queries
* Supports multilingual keywords
* Returns language-specific responses

---

## 🔀 Routing Logic

1. FAQ detected → return FAQ response
2. Order query → return order status
3. Strong negative sentiment → escalate to human
4. Otherwise → use Gemini AI

---

## 📡 API Endpoints

### 🔹 Chat API (Frontend Use)

POST `/chat`

Request:
{
"message": "Where is my order?"
}

Response:
{
"reply": "📦 Your order is shipped..."
}

---

### 🔹 WhatsApp Webhook

POST `/webhook`

Used by Twilio for WhatsApp integration

---

## ⚙️ Setup Instructions (For Team)

### 1. Clone Repository

git clone <repo-link>
cd AI_SYSTEM

---

### 2. Install Dependencies

pip install -r requirements.txt

---

### 3. Create `.env` file

GOOGLE_API_KEY=your_api_key_here

---

### 4. Run Backend

uvicorn main:app --reload

---

### 5. Test API

Use Postman or frontend:

POST http://localhost:8000/chat

---

## 🧪 Sample Test Queries

### English

* Where is my order?

### Hindi

* मेरा ऑर्डर कहाँ है?

### Tamil

* என் ஆர்டர் எங்கே?

### Bengali

* আমার অর্ডার কোথায়?

### Angry Query

* This is worst service!

---

## 🧠 Design Decisions

* Used pretrained models instead of training from scratch
* Added rule-based overrides for multilingual accuracy
* Combined AI + rule-based system for reliability
* Implemented fallback to prevent crashes

---

## 🔐 Environment Variables

| Variable       | Description    |
| -------------- | -------------- |
| GOOGLE_API_KEY | Gemini API key |

---

## 👨‍💻 For Frontend Team

Use this API:

fetch("http://localhost:8000/chat", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ message: "Hi" })
})
.then(res => res.json())
.then(data => console.log(data.reply));

---

## 🚀 Future Improvements

* Add real database (PostgreSQL)
* Replace rule-based with trained intent model
* Add live agent dashboard
* Deploy on cloud (Render / AWS)

---

## 🧠 Key Highlights

* Hybrid AI architecture (rule + ML)
* Multilingual NLP handling
* Fault-tolerant system design
* Scalable backend

---

## 👨‍🎓 Author

Ashutosh Pradhan
B.Tech CSE (AI & ML)

---
