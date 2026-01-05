import streamlit as st
import requests
import json

# 1. Design & Branding
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 ArslanTV AI")

# 2. Key Check (Aus deinen Secrets)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("API-Key fehlt in den Secrets!")
    st.stop()

api_key = st.secrets["GOOGLE_API_KEY"]

# 3. Chat-Verlauf
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Die "Manuelle" KI-Logik (Bypass für den 404-Fehler)
def ask_google_direct(prompt):
    # WICHTIG: Wir nutzen hier 'v1' statt 'v1beta' -> Das ist der Trick!
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # Falls Flash nicht geht, probieren wir das Pro-Modell
            fallback_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
            response = requests.post(fallback_url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"Fehler: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Verbindungsfehler: {e}"

# 5. Eingabe verarbeiten
if prompt := st.chat_input("Wie kann ich Ihnen helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Antwort holen
    answer = ask_google_direct(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
