import streamlit as st
import google.generativeai as genai

# Design-Einstellungen
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 ArslanTV AI")
st.write("Ihr Profi-KI-Assistent.")

# API-Key laden
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# Chat-Historie
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# KI-Logik
if prompt := st.chat_input("Schreiben Sie etwas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Diese Schreibweise ist die stabilste gegen 404-Fehler
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        full_response = response.text
        with st.chat_message("assistant"):
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"Fehler: {e}. Versuche Modell-Wechsel...")
        # Backup-Versuch mit Pro-Modell falls Flash im Key gesperrt ist
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            st.chat_message("assistant").markdown(response.text)
        except:
            st.error("Bitte prüfe deinen API-Key im Google AI Studio. Er scheint nicht für Gemini 1.5 freigeschaltet zu sein.")
