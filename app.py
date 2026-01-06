import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64

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

# 2. HILFSFUNKTIONEN (AUDIO & DATEIEN)
def speak_text(text):
    """Erzeugt eine Audiodatei aus Text und spielt sie ab."""
    tts = gTTS(text=text, lang='de')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_b64 = base64.b64encode(fp.read()).decode()
    audio_html = f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">'
    st.markdown(audio_html, unsafe_allow_html=True)

def process_upload(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        return f"\n\n[PDF-Inhalt]:\n{text}"
    elif file.type in ["image/png", "image/jpeg", "image/jpg"]:
        return Image.open(file)
    return None

# 3. SIDEBAR
with st.sidebar:
    st.title("🚀 ArslanTV Zentrale")
    model_choice = st.selectbox(
        "Wähle dein Modell:",
        ["models/gemini-2.0-flash", "models/gemini-3-pro-preview", 
         "models/gemini-3-flash-preview", "models/nano-banana-pro-preview",
         "models/deep-research-pro-preview-12-2025"]
    )
    enable_voice = st.checkbox("Live-Audio (Sprachausgabe)", value=True)
    st.write("---")
    uploaded_file = st.file_uploader("Datei hochladen", type=["pdf", "png", "jpg"])
    if st.button("🗑️ Chat löschen"):
        st.session_state.messages = []
        st.rerun()

# 4. HAUPTFENSTER
st.title("ArslanTV AI")
st.caption(" Ihr Premium KI-Assistent")
st.write("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. CHAT-LOGIK
if prompt := st.chat_input("Schreibe ArslanTV AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        model = genai.GenerativeModel(model_choice)
        content_to_send = [prompt]
        
        if uploaded_file:
            processed = process_upload(uploaded_file)
            if isinstance(processed, str): content_to_send[0] += processed
            else: content_to_send.append(processed)

        with st.spinner("ArslanTV AI antwortet..."):
            response = model.generate_content(content_to_send)
            
            if response.text:
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                if enable_voice:
                    speak_text(response.text)
            
    except Exception as e:
        st.error(f"Fehler: {e}")
