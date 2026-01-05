import streamlit as st
import google.generativeai as genai

# Design
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 ArslanTV AI")

# API-Key Sicherung
if "GOOGLE_API_KEY" in st.secrets:
    # WICHTIG: Wir konfigurieren hier die API ganz explizit
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte API-Key in den Secrets prüfen!")
    st.stop()

# Chat-Verlauf
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# KI Logik
if prompt := st.chat_input("Wie kann ich Ihnen helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Wir nutzen hier eine stabilere Methode für den Modellaufruf
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Wir erzwingen die Antwort
        response = model.generate_content(prompt)
        
        if response:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    except Exception as e:
        # Falls der 404-Fehler wieder auftaucht, versuchen wir es über den 'models/' Pfad
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            response = model.generate_content(prompt)
            st.chat_message("assistant").markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.error("Google Server Antwort: Bitte die App in 2 Minuten einmal 'Rebooten'.")
