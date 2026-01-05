import streamlit as st
import requests
import json

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    .success-msg { color: #00ff00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 ArslanTV AI")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("API-Key fehlt in den Secrets!")
    st.stop()

api_key = st.secrets["GOOGLE_API_KEY"]

# --- 2. INTELLIGENTER AUTO-SCANNER ---
def ask_google_smart(prompt):
    # Diese Liste enthält alle möglichen Schreibweisen, die Google akzeptiert
    # Der Code probiert sie nacheinander durch, bis einer klappt.
    candidate_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-pro",
        "gemini-1.0-pro"
    ]

    last_error = ""

    for model_name in candidate_models:
        # Wir testen sowohl die v1beta als auch die v1 Schnittstelle
        for version in ["v1beta", "v1"]:
            url = f"https://generativelanguage.googleapis.com/{version}/models/{model_name}:generateContent?key={api_key}"
            
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    # TREFFER! Wir haben das richtige Modell gefunden
                    return response.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    last_error = response.text
            except Exception as e:
                last_error = str(e)
                continue
    
    # Wenn gar nichts klappt, zeigen wir den letzten Fehler
    return f"Fehler: Kein Modell gefunden. Letzte Meldung von Google: {last_error}"

# --- 3. CHAT LOGIK ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Wie kann ich Ihnen helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Hier rufen wir den Scanner auf
    with st.spinner("KI sucht funktionierendes Modell..."):
        answer = ask_google_smart(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
