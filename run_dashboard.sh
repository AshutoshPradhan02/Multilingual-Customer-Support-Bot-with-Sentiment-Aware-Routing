#!/bin/bash
echo "Starting Multilingual Customer Support Dashboard..."
cd "$(dirname "$0")/sentiment_dashboard" || exit
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
