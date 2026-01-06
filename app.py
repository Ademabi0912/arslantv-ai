import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. SETUP & BRANDING ---
st.set_page_config(page_title="ArslanTV AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    .stSidebar { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Key fehlt!")
    st.stop()

# --- 2. HILFSFUNKTIONEN ---
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='de')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">', unsafe_allow_html=True)
    except: pass

def process_file(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "".join([p.extract_text() for p in reader.pages])
        return Image.open(file)
    except: return None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🚀 ArslanTV Zentrale")
    # Hier sind die korrigierten Namen für maximale Stabilität
    model_choice = st.selectbox("Modell wählen:", [
        "gemini-1.5-flash", # Stabilster Pfad ohne 'models/' Präfix für manche API-Versionen
        "gemini-2.0-flash-exp",
        "gemini-3-pro-preview",
        "nano-banana-pro-preview"
    ])
    enable_voice = st.checkbox("Live-Audio (Vorlesen)", value=True)
    uploaded_file = st.file_uploader("Datei hochladen", type=["pdf", "png", "jpg"])
    if st.button("🗑️ Chat löschen"):
        st.session_state.messages = []
        st.rerun()

# --- 4. INTERFACE ---
st.title("ArslanTV AI")
st.caption(" Ihr Premium KI-Assistent")
st.write("---")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- 5. LOGIK MIT VERBESSERTEM RETTUNGSSYSTEM ---
if prompt := st.chat_input("Schreibe ArslanTV AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    content = [prompt]
    if uploaded_file:
        proc = process_file(uploaded_file)
        if isinstance(proc, str): content[0] += "\n" + proc
        elif proc: content.append(proc)

    with st.chat_message("assistant"):
        res_text = ""
        # LISTE DER MODELLE ZUM DURCHPROBIEREN (FALLBACK-KETTE)
        model_attempts = [model_choice, "gemini-1.5-flash", "gemini-pro"]
        
        for current_model_name in model_attempts:
            try:
                model = genai.GenerativeModel(current_model_name)
                response = model.generate_content(content)
                res_text = response.text
                if res_text: break # Erfolg!
            except Exception as e:
                continue # Nächstes Modell probieren
        
        if res_text:
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            if enable_voice: speak_text(res_text)
        else:
            st.error("Alle Modelle sind derzeit überlastet. Bitte versuche es in ein paar Minuten erneut.")
