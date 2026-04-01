import streamlit as st
import pandas as pd
import sys
import os

# Ensure the database module can be imported correctly from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import db_client

# ---- PAGE SETUP ----
st.set_page_config(
    page_title="Human Agent Portal",
    page_icon="👨‍💼",
    layout="wide",
)

st.markdown("""
    <style>
    .main { background-color: transparent; }
    h1, h2, h3 { color: #ffffff !important; }
    .ticket-header { font-size: 18px; font-weight: 600; color: #ffffff; }
    .critical-badge { background-color: #fee2e2; color: #ef4444; border-radius: 999px; padding: 2px 8px; font-size: 12px; font-weight: bold; }
    .urgent-badge { background-color: #fef3c7; color: #d97706; border-radius: 999px; padding: 2px 8px; font-size: 12px; font-weight: bold; }
    .lang-badge { background-color: #e0e7ff; color: #4f46e5; border-radius: 999px; padding: 2px 8px; font-size: 12px; font-weight: bold; }
    .context-label { font-size: 13px; font-weight: 600; color: #d1d5db; text-transform: uppercase; }
    .context-value { font-size: 15px; color: #ffffff; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("👨‍💼 Human Agent Interaction Portal")
st.markdown("Handle complex queries and escalated customers who require human intervention.")

# Initialize session state for temporarily simulated resolves
if 'resolved_tickets' not in st.session_state:
    st.session_state.resolved_tickets = set()

# Fetch all escalated tickets
escalated_df = db_client.df[db_client.df['status'] == 'escalated']
# Filter out the tickets we've supposedly resolved in this session
escalated_df = escalated_df[~escalated_df['ticket_id'].isin(st.session_state.resolved_tickets)]

if escalated_df.empty:
    st.success("🎉 All escalated tickets have been resolved! Great job.")
    st.stop()

st.header(f"Active Escalations ({len(escalated_df)})")

# Let's display the top 20 for performance
for index, row in escalated_df.head(20).iterrows():
    
    # Determine badge color based on sentiment/urgency
    badge = f'<span class="critical-badge">🔴 {row["escalation_reason"].replace("_", " ").title()}</span>' \
        if row["sentiment"] == 'NEGATIVE' or row["urgency"] == 'critical' \
        else f'<span class="urgent-badge">🟠 {row["escalation_reason"].replace("_", " ").title()}</span>'
        
    lang = f'<span class="lang-badge">🌍 {row["language"].upper()}</span>'
    
    title_html = f"Ticket #{row['ticket_id']} &nbsp; {badge} &nbsp; {lang}"
    
    with st.expander(f"Ticket #{row['ticket_id']} - {row['sentiment']} Sentiment ({row['created_at'].strftime('%I:%M %p')})"):
        
        st.markdown(f"**Customer Message:**", unsafe_allow_html=True)
        st.info(f'"{row["user_message"]}"')
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="context-label">Detected Intent</div><div class="context-value">{row["intent"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="context-label">AI Sentiment Score</div><div class="context-value">{(row["sentiment_score"] * 100):.1f}% Confidence</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="context-label">Wait Time</div><div class="context-value">{(pd.Timestamp.now() - row["created_at"]).components.hours}h {(pd.Timestamp.now() - row["created_at"]).components.minutes}m</div>', unsafe_allow_html=True)
            
        st.markdown("### Prepare AI Context Summary")
        # Simulating a context summary to help the human agent
        st.write(f"The user is reaching out regarding their **{row['intent'].replace('_', ' ')}**. The bot failed to resolve this autonomously because the sentiment was highly **{row['sentiment'].lower()}** (Reason: {row['escalation_reason']}). Please process their request manually.")
        
        reply = st.text_area("Your Response", key=f"reply_{row['ticket_id']}")
        
        if st.button("Resolve Ticket", type="primary", key=f"btn_{row['ticket_id']}"):
            st.session_state.resolved_tickets.add(row['ticket_id'])
            st.success(f"Ticket #{row['ticket_id']} marked as resolved!")
            st.rerun()
