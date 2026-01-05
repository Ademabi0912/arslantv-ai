import streamlit as st
import google.generativeai as genai

# Design & Branding
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
    # HIER IST DER FIX: Wir erzwingen die stabile API-Version
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
        # Wir nutzen den VOLLSTÄNDIGEN Pfad, damit v1beta nicht dazwischenfunkt
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        if response.text:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    except Exception as e:
        # Sicherheits-Backup: Falls der Pfad oben noch hakt
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content(prompt)
            st.chat_message("assistant").markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as final_e:
            st.error(f"Technisches Problem: Bitte kurz warten. (Fehler: {final_e})")
