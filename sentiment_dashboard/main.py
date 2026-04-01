import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database import db_client

# ---- PAGE SETUP ----
# Setting layout to wide to utilize screen space, and defining the Light theme via config
st.set_page_config(
    page_title="Multilingual Support Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Light Theme CSS Override (to ensure it feels bright and modern)
st.markdown("""
    <style>
    .main {
        background-color: transparent;
    }
    .metric-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        text-align: center;
        border: 1px solid #374151;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin: 5px 0;
    }
    .metric-label {
        font-size: 14px;
        font-weight: 500;
        color: #d1d5db;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-trend-up { color: #34d399; font-weight: 600; font-size: 13px; }
    .metric-trend-down { color: #f87171; font-weight: 600; font-size: 13px; }
    h1, h2, h3 { color: #ffffff !important; }
    .stDataFrame { border-radius: 10px !important; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)


# ---- TITLE ----
st.title("🤖 Multilingual Support Command Center")
st.markdown("Monitor real-time resolution rates, sentiment trends, and human escalations.")

# Space to force visual breathing room
st.markdown("<br>", unsafe_allow_html=True)

# Fetch data via database client
metrics = db_client.get_summary_metrics()

# ---- SECTION 1: OVERVIEW METRIC CARDS ----
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Messages</div>
            <div class="metric-value">{metrics['total_tickets']:,}</div>
            <div class="metric-trend-up">↑ 12% vs yesterday</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Automated Resolution</div>
            <div class="metric-value" style="color: #2563eb;">{metrics['automation_rate']}%</div>
            <div class="metric-trend-up">↑ target > 70%</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Escalation Rate</div>
            <div class="metric-value" style="color: #ea580c;">{metrics['escalation_rate']}%</div>
            <div class="metric-trend-down">↓ 2.1% less than avg</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Escalations</div>
            <div class="metric-value" style="color: #dc2626;">{metrics['active_tickets']:,}</div>
            <div class="metric-trend-down">Human agents required</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# ---- SECTION 2: CHARTS ----
st.header("📊 Performance Analytics")

c1, c2 = st.columns(2)

with c1:
    # 1. Sentiment Distribution (Pie Chart)
    sentiment_data = db_client.get_sentiment_distribution()
    color_map = {"POSITIVE": "#10b981", "NEUTRAL": "#9ca3af", "NEGATIVE": "#ef4444"}
    
    fig_sentiment = px.pie(
        sentiment_data, 
        values='count', 
        names='sentiment', 
        title="Overall Customer Sentiment",
        color='sentiment',
        color_discrete_map=color_map,
        hole=0.4
    )
    fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
    fig_sentiment.update_layout(margin=dict(t=40, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_sentiment, use_container_width=True)

with c2:
    # 2. Languages Distribution (Donut Chart)
    lang_data = db_client.get_language_distribution()
    lang_mapping = {"en": "English", "es": "Spanish", "hi": "Hindi"}
    lang_data['Language'] = lang_data['language'].map(lang_mapping)
    
    fig_lang = px.pie(
        lang_data, 
        values='count', 
        names='Language', 
        title="Language Distribution",
        hole=0.4,
        color_discrete_sequence=['#3b82f6', '#8b5cf6', '#ec4899']
    )
    fig_lang.update_layout(margin=dict(t=40, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_lang, use_container_width=True)


col_c3, col_c4 = st.columns(2)

with col_c3:
    # 3. Top Customer Issues / Intents (Bar Chart)
    intent_data = db_client.get_intent_distribution()
    fig_intents = px.bar(
        intent_data.head(5), 
        x='intent', 
        y='count', 
        title="Top 5 Customer Queries",
        color='count',
        color_continuous_scale="Blues"
    )
    fig_intents.update_layout(xaxis_title="Intent", yaxis_title="Volume", margin=dict(t=40, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_intents, use_container_width=True)

with col_c4:
    # 4. Volume Over Time (Line Chart)
    volume_data = db_client.get_volume_over_time()
    fig_vol = px.line(
        volume_data, 
        x='hour', 
        y='count', 
        title="Message Volume (Time Series)",
        markers=True
    )
    fig_vol.update_traces(line_color='#2563eb', line_width=2)
    fig_vol.update_layout(xaxis_title="Time", yaxis_title="Number of Messages", margin=dict(t=40, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_vol, use_container_width=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# ---- SECTION 3: LIVE RECENT TICKETS FEED ----
st.header("🚨 Live Ticket Feed")

filter_status = st.radio(
    "Filter Ticket Status:",
    options=["All", "Escalated", "Resolved by Bot"],
    horizontal=True,
    index=1  # Default to seeing what needs human attention
)

recent_tickets = db_client.get_recent_tickets(limit=15, status_filter=filter_status)

# Format the dataframe display
# We could use `st.dataframe` to style things directly
def color_sentiment(val):
    color = '#10b981' if val == 'POSITIVE' else '#ef4444' if val == 'NEGATIVE' else '#9ca3af'
    return f'color: {color}; font-weight: bold'

def color_status(val):
    color = '#ef4444' if val == 'escalated' else '#2563eb'
    return f'color: {color}; font-weight: bold'

styled_df = recent_tickets.style.map(color_sentiment, subset=['sentiment'])\
                              .map(color_status, subset=['status'])

st.dataframe(
    styled_df, 
    use_container_width=True,
    hide_index=True,
    column_config={
        "ticket_id": st.column_config.NumberColumn("ID", format="%d"),
        "user_message": st.column_config.TextColumn("Message", width="large"),
        "language": "Lang",
        "intent": "Detected Intent",
        "sentiment": "Sentiment",
        "status": "Resolution Status",
        "created_at": st.column_config.DatetimeColumn("Timestamp", format="hh:mm A")
    }
)
