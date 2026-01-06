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
    .coin-box { padding: 10px; border-radius: 10px; background: #21262d; border: 1px solid #e3b341; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. COIN LOGIK ---
if "user_coins_pro" not in st.session_state:
    st.session_state.user_coins_pro = 50  # Startguthaben für Pro-Modelle (wie bei Gemini Free)

# --- 3. HILFSFUNKTIONEN ---
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
            return "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        return Image.open(file)
    except: return None

# --- 4. SIDEBAR MIT COIN-ANZEIGE ---
with st.sidebar:
    st.title("🚀 ArslanTV Zentrale")
    
    # Coin Anzeige
    st.markdown('<div class="coin-box">', unsafe_allow_html=True)
    st.write("🪙 **Dein Guthaben**")
    st.write(f"Standard: ∞ (Unendlich)")
    st.write(f"Pro-Modelle: {st.session_state.user_coins_pro} Coins")
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")

    model_choice = st.selectbox("Modell wählen:", [
        "gemini-1.5-flash", 
        "gemini-2.0-flash-exp",
        "gemini-3-pro-preview",
        "nano-banana-pro-preview"
    ])
    
    enable_voice = st.checkbox("Live-Audio (Vorlesen)", value=True)
    uploaded_file = st.file_uploader("Datei hochladen", type=["pdf", "png", "jpg"])
    
    if st.button("🗑️ Chat & Coins Reset"):
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

# --- 6. LOGIK MIT COIN-ABZUG ---
if prompt := st.chat_input("Schreibe ArslanTV AI..."):
    # Prüfen ob Pro-Coins reichen
    is_pro = "pro" in model_choice.lower() or "3" in model_choice
    
    if is_pro and st.session_state.user_coins_pro <= 0:
        st.warning("⚠️ Deine Pro-Coins sind leer! Wechsle zu einem Standard-Modell (∞).")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        content = [prompt]
        if uploaded_file:
            proc = process_file(uploaded_file)
            if isinstance(proc, str): content[0] += "\n" + proc
            elif proc: content.append(proc)

        with st.chat_message("assistant"):
            res_text = ""
            model_queue = [model_choice, "gemini-1.5-flash"]
            
            for attempt_name in model_queue:
                try:
                    model = genai.GenerativeModel(attempt_name)
                    response = model.generate_content(content)
                    res_text = response.text
                    if res_text:
                        # Coins abziehen wenn Pro erfolgreich war
                        if is_pro and attempt_name == model_choice:
                            st.session_state.user_coins_pro -= 1
                        break
                except Exception:
                    continue
            
            if res_text:
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                if enable_voice: speak_text(res_text)
                st.rerun() # UI aktualisieren für Coin-Anzeige
            else:
                st.error("Limit erreicht. Versuche es später erneut.")
