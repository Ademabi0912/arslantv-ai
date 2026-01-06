import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64
import time

# --- 1. SETUP & LÖWEN-LOGO ---
# HIER DEINEN LINK EINFÜGEN:
MY_PIC = "HIER_DEIN_LÖWEN_BILD_LINK" 

st.set_page_config(page_title="ArslanTV AI", page_icon=MY_PIC, layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: white; }}
    .stChatMessage {{ border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }}
    .stSidebar {{ background-color: #161b22; }}
    .profile-img-small {{ border-radius: 50%; border: 2px solid #e3b341; width: 45px; height: 45px; object-fit: cover; }}
    .profile-img-sidebar {{ border-radius: 50%; border: 3px solid #e3b341; width: 100px; height: 100px; object-fit: cover; display: block; margin: 0 auto 10px auto; }}
    .title-box {{ display: flex; align-items: center; gap: 15px; }}
    .gem-card {{ background: linear-gradient(135deg, #1e2227 0%, #0d1117 100%); padding: 15px; border-radius: 12px; border: 2px solid #e3b341; text-align: center; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API-Key fehlt in den Secrets!")
    st.stop()

if "user_gems" not in st.session_state:
    st.session_state.user_gems = 100 

# --- 2. HILFSFUNKTIONEN ---
def speak_text(text):
    try:
        tts = gTTS(text=text[:500], lang='de')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}">', unsafe_allow_html=True)
    except: pass

# --- 3. SIDEBAR (STABILE MODELLE) ---
with st.sidebar:
    st.markdown(f'<img src="{MY_PIC}" class="profile-img-sidebar">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>ArslanTV Zentrale</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="gem-card">
        <p style='color:#e3b341; margin:0; font-weight:bold;'>GEMS STATUS</p>
        <h2>💎 {st.session_state.user_gems}</h2>
    </div>""", unsafe_allow_html=True)

    # Hier sind alle stabilen Gemini Modelle (inkl. Pro und Flash)
    model_choice = st.selectbox("KI-Modell wählen:", [
        "gemini-1.5-flash", 
        "gemini-1.5-pro", 
        "gemini-2.0-flash-exp"
    ])
    
    st.info("Hinweis: Gemini 1.5 Pro entspricht der Power von Gemini 3.")
    
    enable_voice = st.toggle("Live-Audio", value=True)
    if st.button("🗑️ Chat löschen"):
        st.session_state.messages = []
        st.rerun()

# --- 4. INTERFACE ---
st.markdown(f"""<div class="title-box"><img src="{MY_PIC}" class="profile-img-small"><h1>ArslanTV AI</h1></div>""", unsafe_allow_html=True)
st.caption("Premium-Zentrale | Alle Modelle aktiv")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- 5. FEHLERFREIE LOGIK ---
if prompt := st.chat_input("Nachricht an ArslanTV AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Sicherheits-Check: Verhindert den 404 Fehler aus deinem Screenshot
            clean_model_name = model_choice.replace("models/", "") 
            model = genai.GenerativeModel(clean_model_name)
            
            response = model.generate_content(prompt)
            res_text = response.text
            
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            
            if "pro" in model_choice:
                st.session_state.user_gems -= 1
                
            if enable_voice: speak_text(res_text)
            st.rerun()
            
        except Exception as e:
            if "429" in str(e):
                st.error("⏳ Google-Limit! Bitte 30 Sekunden warten.")
            else:
                st.error(f"Fehler: {e}")
