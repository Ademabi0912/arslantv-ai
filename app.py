import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    .stSidebar { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# API-Key laden
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ API-Key fehlt in den Secrets!")
    st.stop()

# --- 2. FUNKTIONEN (AUDIO & FILES) ---
def speak_text(text):
    """Liest den Text vor (Fehler-Tolerant)"""
    try:
        if not text.strip(): return
        tts = gTTS(text=text, lang='de')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">'
        st.markdown(audio_html, unsafe_allow_html=True)
    except:
        pass # Falls Audio fehlschlägt, stumm weitermachen

def process_file(file):
    """Verarbeitet PDFs und Bilder"""
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return f"\n\n[PDF-Inhalt]:\n{text}"
        elif file.type in ["image/png", "image/jpeg", "image/jpg"]:
            return Image.open(file)
    except:
        return None
    return None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🚀 ArslanTV Zentrale")
    
    # Deine Wunsch-Liste
    selected_model_name = st.selectbox(
        "Wähle dein Modell:",
        [
            "models/gemini-2.0-flash",
            "models/gemini-3-pro-preview",
            "models/nano-banana-pro-preview",
            "models/deep-research-pro-preview-12-2025",
            "models/gemini-1.5-pro"
        ]
    )
    
    enable_voice = st.checkbox("🔊 Live-Audio (Vorlesen)", value=True)
    st.write("---")
    uploaded_file = st.file_uploader("Datei hochladen (Bild/PDF)", type=["pdf", "png", "jpg", "jpeg"])
    
    if st.button("🗑️ Chat löschen"):
        st.session_state.messages = []
        st.rerun()

# --- 4. HAUPT-INTERFACE ---
st.title("ArslanTV AI")
st.caption(" Ihr Premium KI-Assistent")
st.write("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. INTELLIGENTE KI-LOGIK (MIT ABSTURZ-SCHUTZ) ---
if prompt := st.chat_input("Schreibe ArslanTV AI..."):
    # User Nachricht
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Daten vorbereiten
    content_to_send = [prompt]
    if uploaded_file:
        processed_data = process_file(uploaded_file)
        if processed_data:
            if isinstance(processed_data, str): content_to_send[0] += processed_data # PDF
            else: content_to_send.append(processed_data) # Bild

    # Die Magie: Versuch macht klug
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 1. Versuch: Das gewünschte Modell (z.B. Nano Banana)
            with st.spinner(f"Verbinde mit {selected_model_name}..."):
                model = genai.GenerativeModel(selected_model_name)
                response = model.generate_content(content_to_send)
                full_response = response.text

        except Exception as e:
            # 2. Versuch: FALLBACK (Der Rettungsschirm)
            # Wenn das Wunschmodell nicht geht, nehmen wir automatisch das stabilste Modell
            try:
                fallback_model = "models/gemini-1.5-flash"
                model = genai.GenerativeModel(fallback_model)
                response = model.generate_content(content_to_send)
                full_response = response.text
                # Kleiner Hinweis, aber KEIN Fehler
                st.caption(f"ℹ️ Hinweis: {selected_model_name} ist gerade ausgelastet. Antwort kommt von Backup (Flash).")
            except Exception as e2:
                full_response = "Entschuldigung, ich habe gerade Verbindungsprobleme. Bitte lade die Seite neu."

        # Antwort anzeigen
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Audio abspielen (wenn aktiviert)
        if enable_voice and full_response:
            speak_text(full_response)
