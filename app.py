import streamlit as st
import google.generativeai as genai

# 1. Design & Seiteneinstellungen
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖", layout="centered")

# Schickes CSS für dunkles Design und runde Ecken
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("ArslanTV AI")
st.caption("Ihr Profi-KI-Assistent für alle Antworten.")

# 2. API-Key sicher laden
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte API-Key in den Streamlit Secrets hinterlegen!")
    st.stop()

# 3. Das richtige Modell wählen (Stabilere Version)
try:
    # Wir nutzen 'gemini-1.5-flash' - das ist schnell und aktuell
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Modell-Fehler: {e}")

# 4. Chat-Verlauf speichern
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. Eingabe und Antwort
if prompt := st.chat_input("Wie kann ich Ihnen heute helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        # Hier wird die Antwort generiert
        response = model.generate_content(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"KI-Fehler: {e}. Bitte prüfen Sie, ob der API-Key korrekt ist.")

