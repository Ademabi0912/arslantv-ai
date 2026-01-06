import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. SETUP & PERSONALISIERUNG ---
# Link zu deinem Löwen-Profilbild (Gmail)
MY_PIC = "https://lh3.googleusercontent.com/a/ACg8ocL8_Q3H4_Y9_Y9_Y9_Y9" # Beispiel-Struktur

st.set_page_config(page_title="ArslanTV AI", page_icon=MY_PIC, layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: white; }}
    .stChatMessage {{ border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }}
    .stSidebar {{ background-color: #161b22; }}
    
    .profile-img-small {{ border-radius: 50%; border: 2px solid #e3b341; width: 50px; height: 50px; object-fit: cover; }}
    .profile-img-sidebar {{ border-radius: 50%; border: 3px solid #e3b341; width: 100px; height: 100px; object-fit: cover; display: block; margin: 0 auto 10px auto; }}
    
    .title-box {{ display: flex; align-items: center; gap: 15px; }}
    .gem-card {{ background: linear-gradient(135deg, #1e2227 0%, #0d1117 100%); padding: 15px; border-radius: 12px; border: 2px solid #e3b341; text-align: center; margin-bottom: 20px; }}
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

    model_choice = st.selectbox("Modell wählen:", ["gemini-1.5-flash", "gemini-2.0-flash-exp", "models/nano-banana-pro-preview", "models/gemini-3-pro-preview"])
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

# --- 6. KI-LOGIK (VERBESSERT) ---
if prompt := st.chat_input("Frage ArslanTV AI..."):
    is_pro = any(x in model_choice.lower() for x in ["pro", "banana", "3"])
    
    if is_pro and st.session_state.user_gems <= 0:
        st.warning("⚠️ Gems leer!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            res_text = ""
            queue = [model_choice, "gemini-1.5-flash"]
            last_err = ""
            
            for m_name in queue:
                try:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(prompt)
                    res_text = response.text
                    if res_text:
                        if is_pro and m_name == model_choice: st.session_state.user_gems -= 1
                        break
                except Exception as e:
                    last_err = str(e)
                    continue

            if res_text:
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                if enable_voice: speak_text(res_text)
                st.rerun()
            else:
                st.error(f"Google-Limit erreicht. Bitte 60 Sek. warten. (Fehler: {last_err})")
