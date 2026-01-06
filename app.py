import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
import io

# 1. SETUP & DESIGN
st.set_page_config(page_title="ArslanTV AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    .stSidebar { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# API-Key Sicherung
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt in den Secrets!")
    st.stop()

# 2. SIDEBAR - MODELL & DATEI-UPLOAD
with st.sidebar:
    st.title("🚀 ArslanTV Zentrale")
    
    # Modell-Auswahl basierend auf deiner Liste
    model_choice = st.selectbox(
        "Wähle dein Modell:",
        [
            "models/gemini-2.0-flash", 
            "models/gemini-3-pro-preview", 
            "models/gemini-3-flash-preview",
            "models/nano-banana-pro-preview",
            "models/deep-research-pro-preview-12-2025",
            "models/gemini-1.5-pro"
        ]
    )
    
    st.write("---")
    st.header("📂 Datei-Upload")
    uploaded_file = st.file_uploader("PDF oder Bild hochladen", type=["pdf", "png", "jpg", "jpeg"])
    
    if st.button("🗑️ Chat löschen"):
        st.session_state.messages = []
        st.rerun()

# 3. DATEI-VERARBEITUNG LOGIK
def process_upload(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return f"\n\n[Inhalt der PDF-Datei]:\n{text}"
    elif file.type in ["image/png", "image/jpeg", "image/jpg"]:
        return Image.open(file)
    return None

# 4. CHAT-INTERFACE (DEINE ÄNDERUNGEN)
st.title("ArslanTV AI")
st.caption("Ihr Premium KI-Assistent")
st.write(f"---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. KI-ANFRAGE
if prompt := st.chat_input("Frage stellen oder Datei beschreiben..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        model = genai.GenerativeModel(model_choice)
        content_to_send = [prompt]
        
        if uploaded_file:
            processed = process_upload(uploaded_file)
            if isinstance(processed, str): # PDF Text
                content_to_send[0] += processed
            else: # Bild
                content_to_send.append(processed)

        with st.spinner("ArslanTV AI denkt nach..."):
            response = model.generate_content(content_to_send)
            
            if response.text:
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    except Exception as e:
        st.error(f"Fehler: {e}")
