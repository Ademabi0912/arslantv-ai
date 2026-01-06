import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64
import time

# --- 1. SETUP & BRANDING ---
st.set_page_config(page_title="ArslanTV AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    .stSidebar { background-color: #161b22; }
    .coin-box { padding: 10px; border-radius: 10px; background: #21262d; border: 1px solid #e3b341; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt in den Secrets!")
    st.stop()

# --- 2. SESSION STATE (COINS) ---
if "user_coins_pro" not in st.session_state:
    st.session_state.user_coins_pro = 50 

# --- 3. FUNKTIONEN ---
def speak_text(text):
    try:
        tts = gTTS(text=text[:500], lang='de') # Kürzen für schnellere Antwort
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
            return "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        return Image.open(file)
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 ArslanTV Zentrale")
    
    st.markdown('<div class="coin-box">', unsafe_allow_html=True)
    st.write("🪙 **Dein Guthaben**")
    st.write(f"Standard: ∞ (Unendlich)*")
    st.write(f"Pro-Modelle: {st.session_state.user_coins_pro} Coins")
    st.caption("*Google Rate-Limits beachten")
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")

    model_choice = st.selectbox("Modell wählen:", [
        "gemini-1.5-flash", 
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-pro"
    ])
    
    enable_voice = st.checkbox("Live-Audio (Vorlesen)", value=True)
    uploaded_file = st.file_uploader("Datei hochladen", type=["pdf", "png", "jpg"])
    
    if st.button("🗑️ Reset Chat & Coins"):
        st.session_state.messages = []
        st.session_state.user_coins_pro = 50
        st.rerun()

# --- 5. INTERFACE ---
st.title("ArslanTV AI")
st.caption(" Ihr Premium KI-Assistent")
st.write("---")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- 6. INTELLIGENTE LOGIK ---
if prompt := st.chat_input("Schreibe ArslanTV AI..."):
    is_pro = "pro" in model_choice.lower()
    
    if is_pro and st.session_state.user_coins_pro <= 0:
        st.warning("⚠️ Keine Pro-Coins mehr! Bitte nutze ein Standard-Modell.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Content vorbereiten
        content = [prompt]
        if uploaded_file:
            proc = process_file(uploaded_file)
            if isinstance(proc, str): content[0] += "\n" + proc
            elif proc: content.append(proc)

        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel(model_choice)
                response = model.generate_content(content)
                
                res_text = response.text
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                
                if is_pro: st.session_state.user_coins_pro -= 1
                if enable_voice: speak_text(res_text)
                st.rerun()

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("⏳ Google-Limit erreicht! Bitte warte 30-60 Sekunden, bevor du die nächste Nachricht schickst.")
                elif "404" in error_msg:
                    st.error("📍 Modell nicht verfügbar. Versuche 'gemini-1.5-flash'.")
                else:
                    st.error(f"Fehler: {error_msg}")
