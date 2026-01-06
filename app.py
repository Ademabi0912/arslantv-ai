import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. SETUP & LÖWEN-LOGO ---
# TIPP: Kopiere den Link deines Gmail-Bildes hier hinein:
MY_PIC = "https://lh3.googleusercontent.com/a/ACg8ocL..." # Dein vollständiger Link

st.set_page_config(
    page_title="ArslanTV AI", 
    page_icon=MY_PIC, # Das Bild im Browser-Tab
    layout="wide"
)

# Design für die runden Bilder
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: white; }}
    .profile-img-small {{ border-radius: 50%; border: 2px solid #e3b341; width: 45px; height: 45px; object-fit: cover; }}
    .profile-img-sidebar {{ border-radius: 50%; border: 3px solid #e3b341; width: 100px; height: 100px; object-fit: cover; display: block; margin: 0 auto 10px auto; }}
    .title-box {{ display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)
# --- 2. GEMS SYSTEM ---
if "user_gems" not in st.session_state:
    st.session_state.user_gems = 100 

# --- 3. FUNKTIONEN ---
def speak_text(text):
    try:
        tts = gTTS(text=text[:500], lang='de')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">', unsafe_allow_html=True)
    except: pass

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f'<img src="{MY_PIC}" class="profile-img-sidebar">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>ArslanTV Zentrale</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="gem-card">
        <p style='color:#e3b341; margin:0; font-weight:bold;'>GEMS STATUS</p>
        <h2>💎 {st.session_state.user_gems}</h2>
        <p style='font-size:0.8em; color:#8b949e;'>Standard: ∞ (Unendlich)</p>
    </div>""", unsafe_allow_html=True)

   model_choice = st.selectbox("Modell wählen:", [
    "gemini-1.5-flash", 
    "gemini-2.0-flash-exp", 
    "gemini-1.5-pro"
    "gemini-3.0-pro"
])
    enable_voice = st.toggle("Live-Audio", value=True)
    
    if st.button("🗑️ Reset Chat & Gems"):
        st.session_state.messages = []
        st.session_state.user_gems = 100
        st.rerun()

# --- 5. INTERFACE ---
st.markdown(f"""<div class="title-box"><img src="{MY_PIC}" class="profile-img-small"><h1>ArslanTV AI</h1></div>""", unsafe_allow_html=True)
st.caption("Ihr Premium KI-Assistent | Nano Banana integriert")
st.write("---")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- 6. KI-LOGIK (FINALE VERSION) ---
if prompt := st.chat_input("Frage ArslanTV AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Hier nutzen wir den sauberen Namen ohne "models/"
            model = genai.GenerativeModel(model_choice) 
            response = model.generate_content(prompt)
            res_text = response.text
            
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            if enable_voice: speak_text(res_text)
            st.rerun()
        except Exception as e:
            st.error(f"Verbindung zu Google fehlgeschlagen. Fehler: {e}")
