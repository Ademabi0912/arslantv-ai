import streamlit as st
import google.generativeai as genai

# 1. Design & Interface
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 ArslanTV AI")
st.caption("Status: Verbunden mit Gemini 2.0 Flash")

# 2. API-Key Konfiguration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt in den Streamlit-Secrets!")
    st.stop()

# 3. Chat-Historie
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. KI-Logik (Punktlandung auf das Modell aus deiner Liste)
if prompt := st.chat_input("Schreiben Sie eine Nachricht..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Wir nutzen EXAKT den Pfad aus deinem erfolgreichen System-Check
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        with st.spinner("ArslanTV AI antwortet..."):
            response = model.generate_content(prompt)
            
            if response.text:
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("Keine Textantwort erhalten. Bitte versuche es erneut.")

    except Exception as e:
        st.error(f"Ein kleiner Fehler ist aufgetreten. Bitte Seite neu laden. Details: {e}")
