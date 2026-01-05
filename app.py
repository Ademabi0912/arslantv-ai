import streamlit as st
import google.generativeai as genai

# 1. Konfiguration & UI Styling
st.set_page_config(page_title="ArslanTV Ultimate AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    .stSidebar { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# 2. API-Key Setup
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt! Bitte in den Streamlit-Secrets 'GOOGLE_API_KEY' hinzufügen.")
    st.stop()

# 3. Sidebar: Die "Modell-Garage" (Alle Modelle aus deiner Liste)
with st.sidebar:
    st.title("🚀 Modell-Zentrale")
    
    # Gruppierung der Modelle für bessere Übersicht
    model_category = st.selectbox("Kategorie wählen:", ["Gemini 2.0 (Neu)", "Gemini 1.5 (Standard)", "Experimentell / Spezial"])
    
    if model_category == "Gemini 2.0 (Neu)":
        available_models = [
            "models/gemini-2.0-flash",
            "models/gemini-2.0-flash-001",
            "models/gemini-2.0-flash-exp",
            "models/gemini-2.0-flash-lite-preview-02-05"
        ]
    elif model_category == "Gemini 1.5 (Standard)":
        available_models = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash-latest",
            "models/gemini-pro-latest"
        ]
    else: # Experimentell
        available_models = [
            "models/deep-research-pro-preview-12-2025",
            "models/nano-banana-pro-preview",
            "models/gemini-exp-1206",
            "models/gemini-2.0-flash-exp-image-generation"
        ]
    
    selected_model = st.selectbox("Präpariertes Modell aktivieren:", available_models)
    
    st.write("---")
    if st.button("🗑️ Chat-Verlauf löschen"):
        st.session_state.messages = []
        st.rerun()
    
    st.info(f"Modell-Pfad: {selected_model}")

# 4. Hauptfenster
st.title("🤖 ArslanTV Ultimate AI")
st.markdown(f"Aktive Verbindung: `{selected_model.split('/')[-1]}`")

# Chat-Verlauf Initialisierung
if "messages" not in st.session_state:
    st.session_state.messages = []

# Nachrichten anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. KI Logik & Response
if prompt := st.chat_input("Was soll ArslanTV AI für dich tun?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Modell laden
        model = genai.GenerativeModel(selected_model)
        
        with st.spinner(f"Modell {selected_model.split('/')[-1]} arbeitet..."):
            # Generierung starten
            response = model.generate_content(prompt)
            
            if response.text:
                full_response = response.text
                with st.chat_message("assistant"):
                    st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("Dieses Modell liefert aktuell keine Daten.")
                
    except Exception as e:
        st.error(f"Fehler: Das Modell '{selected_model}' ist unter diesem Namen aktuell nicht erreichbar oder überlastet.")
        st.info("Tipp: Wähle in der Sidebar 'models/gemini-2.0-flash', das ist am stabilsten.")
