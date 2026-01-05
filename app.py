import streamlit as st
import google.generativeai as genai

# 1. Design & Branding
st.set_page_config(page_title="ArslanTV AI - MultiModel", page_icon="🤖")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    </style>
    """, unsafe_allow_html=True)

# 2. API-Key Konfiguration
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte API-Key in den Secrets hinterlegen!")
    st.stop()

# 3. Sidebar für Modell-Auswahl
with st.sidebar:
    st.title("⚙️ Einstellungen")
    # Hier nutzen wir die Namen, die in deiner Liste (Screenshot 17) funktionierten
    selected_model_name = st.selectbox(
        "Wähle dein KI-Modell:",
        [
            "models/gemini-2.0-flash", 
            "models/gemini-1.5-flash", 
            "models/gemini-1.5-pro",
            "models/deep-research-pro-preview-12-2025"
        ],
        help="Gemini 2.0 ist am schnellsten, Deep Research ist am schlausten."
    )
    st.write("---")
    if st.button("Chat löschen"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 ArslanTV AI")
st.caption(f"Aktives Modell: {selected_model_name}")

# 4. Chat-Verlauf
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. KI Logik
if prompt := st.chat_input("Schreibe ArslanTV AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Hier wird das in der Sidebar gewählte Modell geladen
        model = genai.GenerativeModel(selected_model_name)
        
        with st.spinner(f"KI ({selected_model_name.split('/')[-1]}) denkt nach..."):
            response = model.generate_content(prompt)
            
        if response.text:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    except Exception as e:
        st.error(f"Fehler mit diesem Modell: {e}")
        st.info("Probiere ein anderes Modell in der Sidebar aus!")
