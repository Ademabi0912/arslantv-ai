import streamlit as st
import google.generativeai as genai

# Design & Branding
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")

# Dark-Mode Styling
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 ArslanTV AI")
st.markdown("---")

# API-Key Sicherung
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte den GOOGLE_API_KEY in den Streamlit-Secrets hinterlegen.")
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
        # WICHTIG: Wir rufen das Modell OHNE 'models/' Präfix auf, 
        # da die Bibliothek das intern selbst regelt.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generierung der Antwort
        response = model.generate_content(prompt)
        
        if response.text:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        else:
            st.error("Die KI hat keine Antwort geliefert. Prüfen Sie das Kontingent im AI Studio.")
            
    except Exception as e:
        # Falls Gemini 1.5 Flash noch hakt, nutzen wir das bewährte Pro-Modell
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            st.chat_message("assistant").markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.error(f"Kritischer Fehler: {e}")
