import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_dummy_data(num_records=1000):
    """
    Simulates fetching ticket data from PostgreSQL.
    The schema matches the exact requirements for the AI Project:
    - ticket_id: unique identifier
    - user_message: simulated user input
    - language: en, es, hi
    - intent: check_order_status, refund_policy, complaint, etc.
    - sentiment: POSITIVE, NEUTRAL, NEGATIVE
    - sentiment_score: 0.0 to 1.0 confidence
    - urgency: critical, normal
    - status: resolved_by_bot, escalated
    - escalation_reason: urgency, negative_sentiment, low_confidence, None
    - response_time_sec: bot's response latency
    - created_at: timestamp of the interaction
    """
    
    languages = ['en', 'es', 'hi']
    intents = ['check_order_status', 'refund_policy', 'product_query', 'complaint', 'return_request']
    
    # Pre-defined message templates per language/intent
    messages = {
        'en': {
            'check_order_status': ["Where is my order?", "Track my package", "Is my shipment delayed?"],
            'refund_policy': ["How do I get a refund?", "What is your refund policy?", "I want my money back."],
            'product_query': ["Does this come in blue?", "What are the dimensions?", "Is it in stock?"],
            'complaint': ["This is terrible service!", "The item arrived broken.", "I am very angry."],
            'return_request': ["I want to return this.", "How do I send it back?", "Return label please."]
        },
        'es': {
            'check_order_status': ["¿Dónde está mi pedido?", "Rastrear mi paquete"],
            'refund_policy': ["¿Cómo obtengo un reembolso?", "Quiero mi dinero de vuelta"],
            'product_query': ["¿Tienen este en azul?", "¿Está en stock?"],
            'complaint': ["¡Pésimo servicio!", "Llegó roto, estoy furioso"],
            'return_request': ["Quiero devolver esto", "Etiqueta de devolución por favor"]
        },
        'hi': {
            'check_order_status': ["मेरा आर्डर कहाँ है?", "ऑर्डर ट्रैक करें"],
            'refund_policy': ["मुझे रिफंड कैसे मिलेगा?", "पैसे वापस चाहिए"],
            'product_query': ["क्या यह नीले रंग में है?", "स्टॉक में है क्या?"],
            'complaint': ["बहुत खराब सर्विस है!", "गंदा प्रोडक्ट भेजा है"],
            'return_request': ["मुझे वापस करना है", "रिटर्न करना है"]
        }
    }
    
    data = []
    
    # Calculate times backwards from now
    end_date = datetime.now()
    
    for i in range(1, num_records + 1):
        lang = random.choices(languages, weights=[0.6, 0.25, 0.15])[0] # 60% en, 25% es, 15% hi
        intent = random.choices(intents, weights=[0.4, 0.2, 0.25, 0.05, 0.1])[0]
        
        message = random.choice(messages[lang][intent])
        
        # Base logic for sentiment & urgency
        if intent == 'complaint':
            sentiment = 'NEGATIVE'
            score = round(random.uniform(0.85, 0.99), 2)
            urgency = 'critical'
        elif 'refund' in intent or 'return' in intent:
            sentiment = random.choices(['NEGATIVE', 'NEUTRAL'], weights=[0.4, 0.6])[0]
            score = round(random.uniform(0.60, 0.90), 2)
            urgency = 'critical' if sentiment == 'NEGATIVE' and score > 0.8 else 'normal'
        else:
            sentiment = random.choices(['POSITIVE', 'NEUTRAL', 'NEGATIVE'], weights=[0.3, 0.6, 0.1])[0]
            score = round(random.uniform(0.70, 0.95), 2)
            urgency = 'normal'
            
        # Escalation Logic (Simulating exactly the router.py behavior and the 70% autonomous goal)
        if sentiment == 'NEGATIVE' and score > 0.95:
            status = 'escalated'
            reason = 'negative_sentiment'
        elif urgency == 'critical' and random.random() < 0.8:
            status = 'escalated'
            reason = 'urgency'
        elif score < 0.65:
            status = 'escalated'
            reason = 'low_confidence'
        else:
            status = 'resolved_by_bot'
            reason = 'None'
            
        # Times: most replies are fast (0.5 - 2s) but vector DB retrieval might take a bit longer
        response_time = round(random.uniform(0.5, 3.5), 2)
        
        # Random timestamp within the last 7 days
        timestamp = end_date - timedelta(minutes=random.randint(1, 10080))
        
        data.append({
            "ticket_id": i,
            "user_message": message,
            "language": lang,
            "intent": intent,
            "sentiment": sentiment,
            "sentiment_score": score,
            "urgency": urgency,
            "status": status,
            "escalation_reason": reason,
            "response_time_sec": response_time,
            "created_at": timestamp
        })
        
    df = pd.DataFrame(data)
    # Sort by created_at descending (latest first)
    df.sort_values(by='created_at', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df

# Initialize Data Access Object
def get_tickets_data():
    return generate_dummy_data(1500)
    
# Export functions to be consumed by Streamlit
class DatabaseClient:
    def __init__(self):
        # We cache the data instance once so the dashboard isn't changing numbers on every click
        self.df = get_tickets_data()
        
    def get_summary_metrics(self):
        total_tickets = len(self.df)
        escalated = len(self.df[self.df['status'] == 'escalated'])
        automated = total_tickets - escalated
        
        automation_rate = (automated / total_tickets) * 100 if total_tickets > 0 else 0
        avg_response_time = self.df['response_time_sec'].mean()
        
        return {
            "total_tickets": total_tickets,
            "active_tickets": escalated, # Considering escalated as active for human agents
            "automation_rate": round(automation_rate, 1),
            "escalation_rate": round(100 - automation_rate, 1),
            "avg_response_time": round(avg_response_time, 2)
        }
        
    def get_sentiment_distribution(self):
        return self.df['sentiment'].value_counts().reset_index()

    def get_intent_distribution(self):
        return self.df['intent'].value_counts().reset_index()
        
    def get_language_distribution(self):
        return self.df['language'].value_counts().reset_index()
        
    def get_volume_over_time(self):
        # Group by hour for the line chart
        df_time = self.df.copy()
        df_time['hour'] = df_time['created_at'].dt.floor('H')
        return df_time.groupby('hour').size().reset_index(name='count')
        
    def get_escalation_triggers(self):
        escalated_df = self.df[self.df['status'] == 'escalated']
        return escalated_df['escalation_reason'].value_counts().reset_index()
        
    def get_recent_tickets(self, limit=20, status_filter=None):
        filtered_df = self.df
        if status_filter and status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter.lower().replace(" ", "_")]
            
        # Select specific columns to display
        display_cols = ['ticket_id', 'user_message', 'language', 'intent', 'sentiment', 'status', 'created_at']
        return filtered_df[display_cols].head(limit)

# Global client
db_client = DatabaseClient()
