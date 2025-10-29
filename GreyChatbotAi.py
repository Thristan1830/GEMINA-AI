import streamlit as st
import os
import google.generativeai as genai

# Configure API key safely
# You can also set this in Streamlit Secrets for better security
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", "AIzaSyBsfbtaFlzuXr9HPuaz7OJq0k45K6LelKA"))

# Model setup
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""
    Your name is Gray, and you are an AI assistant chatbot for the users.
    Reply to users in a friendly manner.
    Replies should be in English or Filipino depending on what I ask.
    You should only have knowledge about system fundamentals, explain briefly and give a conclusion at the end.
    """,
)

# Streamlit UI
st.set_page_config(page_title="Gray - AI Assistant", page_icon="🤖")
st.title("🤖 Meet Gray – Your AI Assistant")

user_input = st.text_input("Ask Gray anything about system fundamentals:", placeholder="e.g., What is an operating system?")

if st.button("Ask Gray") and user_input:
    with st.spinner("Gray is thinking..."):
        try:
            response = model.generate_content(user_input)
            st.markdown("### 💬 Gray's Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

st.caption("Built with Streamlit and Google's Gemini API")
