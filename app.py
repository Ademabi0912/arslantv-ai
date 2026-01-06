import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. SETUP & PREMIUM DESIGN ---
st.set_page_config(page_title="ArslanTV AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    .stSidebar { background-color: #161b22; }
    .gem-card {
        background: linear-gradient(135deg, #1e2227 0%, #0d1117 100%);
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #e3b341;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt!")
    st.stop()

# --- 2. GEMS SYSTEM ---
if "user_gems" not in st.session_state:
    st.session_state.user_gems = 100 

# --- 3. HILFSFUNKTIONEN ---
def speak_text(text):
    try:
        tts = gTTS(text=text[:500], lang='de')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">', unsafe_allow_html=True)
    except: pass

def process_upload(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        return Image.open(file)
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 ArslanTV Zentrale")
    
    st.markdown(f"""
    <div class="gem-card">
        <p style='color:#e3b341; margin:0; font-weight:bold;'>DEIN GEMS STATUS</p>
        <h2 style='margin:10px 0;'>💎 {st.session_state.user_gems}</h2>
        <p style='font-size:0.8em; color:#8b949e;'>Standard: ∞ Unendlich</p>
    </div>
    """, unsafe_allow_html=True)

    model_choice = st.selectbox("Modell wählen:", [
        "gemini-1.5-flash", 
        "gemini-2.0-flash-exp",
        "models/nano-banana-pro-preview",
        "models/gemini-3-pro-preview",
        "gemini-1.5-pro"
    ])
    
    enable_voice = st.toggle("Live-Audio (Vorlesen)", value=True)
    uploaded_file = st.file_uploader("Datei hochladen", type=["pdf", "png", "jpg"])
    
    if st.button("🗑️ Reset Chat & Gems"):
        st.session_state.messages = []
        st.session_state.user_gems = 100
        st.rerun()

# --- 5. INTERFACE ---
st.title("ArslanTV AI")
st.caption("Ihr Premium KI-Assistent | Nano Banana integriert")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- 6. KI-LOGIK ---
if prompt := st.chat_input("Frage ArslanTV AI..."):
    # Nano Banana und Pro Modelle brauchen Gems
    is_pro = any(x in model_choice.lower() for x in ["pro", "banana", "3"])
    
    if is_pro and st.session_state.user_gems <= 0:
        st.warning("⚠️ Keine Gems mehr für Pro/Banana! Wechsle zu einem Standard-Modell.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        content = [prompt]
        if uploaded_file:
            proc = process_upload(uploaded_file)
            if isinstance(proc, str): content[0] += "\n" + proc
            elif proc: content.append(proc)

        with st.chat_message("assistant"):
            res_text = ""
            # Fallback auf Flash, falls Pro/Banana das Quota-Limit erreicht
            queue = [model_choice, "gemini-1.5-flash"]
            
            for m_name in queue:
                try:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(content)
                    res_text = response.text
                    if res_text:
                        if is_pro and m_name == model_choice:
                            st.session_state.user_gems -= 1
                        break
                except: continue

            if res_text:
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                if enable_voice: speak_text(res_text)
                st.rerun()
            else:
                st.error("Alle Modelle sind gerade überlastet. Bitte kurz warten.")

