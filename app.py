import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="ArslanTV AI Debug", page_icon="🔧", layout="wide")
st.markdown("""<style>.stApp { background-color: #0E1117; color: white; }</style>""", unsafe_allow_html=True)

# API Key Prüfung
if "GOOGLE_API_KEY" in st.secrets:
    key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=key)
    # Kleiner Test: Wir geben die ersten 4 Zeichen des Keys aus, um zu sehen ob er geladen wurde
    st.sidebar.success(f"API-Key geladen: {key[:4]}...*******")
else:
    st.error("CRITICAL ERROR: Kein API-Key in st.secrets gefunden!")
    st.stop()

# --- 2. HILFSFUNKTIONEN ---
def speak_text(text):
    try:
        if not text.strip(): return
        tts = gTTS(text=text, lang='de')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Audio-Fehler (nicht schlimm): {e}")

def process_file(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "".join([p.extract_text() for p in reader.pages])
        elif file.type.startswith("image/"):
            return Image.open(file)
    except: return None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🔧 Diagnose-Zentrale")
    model_choice = st.selectbox("Modell wählen:", [
        "models/gemini-2.0-flash", # Am stabilsten
        "models/gemini-1.5-flash", # Backup
        "models/gemini-3-pro-preview",
        "models/nano-banana-pro-preview"
    ])
    enable_voice = st.checkbox("Audio an", value=False)
    uploaded_file = st.file_uploader("Datei", type=["pdf", "png", "jpg"])
    if st.button("Reset"): st.session_state.messages = []; st.rerun()

# --- 4. CHAT ---
st.title("ArslanTV AI - Debug Modus")
st.caption("Wir finden den Fehler!")

if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Tippe 'test' ein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # DATEN VORBEREITEN
    content = [prompt]
    if uploaded_file:
        proc = process_file(uploaded_file)
        if proc: 
            if isinstance(proc, str): content[0] += "\n" + proc
            else: content.append(proc)

    # --- HIER IST DIE ÄNDERUNG: KEIN VERSTECKEN MEHR ---
    with st.chat_message("assistant"):
        st.write(f"🔄 Versuche Verbindung mit: `{model_choice}`...")
        
        try:
            model = genai.GenerativeModel(model_choice)
            response = model.generate_content(content)
            
            # Wenn wir hier ankommen, hat es geklappt!
            st.success("Verbindung erfolgreich!")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            if enable_voice: speak_text(response.text)

        except Exception as e_main:
            # ERSTER FEHLER
            st.error(f"❌ Fehler mit {model_choice}:")
            st.code(str(e_main)) # Zeigt den exakten Google-Fehlercode
            
            st.write("⚠️ Starte Rettungsversuch mit 'models/gemini-1.5-flash'...")
            
            try:
                fallback = genai.GenerativeModel("models/gemini-1.5-flash")
                response = fallback.generate_content(content)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e_backup:
                # ZWEITER FEHLER (TOTALAUSFALL)
                st.error("❌ Auch das Backup ist gescheitert. Der genaue Fehler ist:")
                st.code(str(e_backup))
                st.warning("BITTE MACHE EINEN SCREENSHOT VON DIESEN ROTEN BOXEN!")
