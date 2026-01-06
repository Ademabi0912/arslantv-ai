import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. PRO-DESIGN (CSS) ---
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    /* Hintergrund und Schrift */
    .stApp { background-color: #0b0e11; color: #e9eaeb; }
    
    /* Chat-Eingabefeld stylen */
    .stChatInputContainer { padding-bottom: 20px; }
    
    /* Sidebar Styling */
    .stSidebar { background-color: #111518 !important; border-right: 1px solid #2d333b; }
    
    /* Coins & Status Box */
    .status-card {
        background: linear-gradient(145deg, #1e2227, #14171a);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    
    /* Nachrichten-Bubbles */
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; border: 1px solid #21262d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK & API ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte füge deinen API-Key in den Streamlit Secrets hinzu!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pro_coins" not in st.session_state:
    st.session_state.pro_coins = 50

# --- 3. SIDEBAR (STEUERUNG) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("ArslanTV Zentrale")
    
    st.markdown(f"""
    <div class="status-card">
        <p style='color:#8b949e; margin:0;'>DEIN GUTHABEN</p>
        <h3 style='margin:0;'>🪙 {st.session_state.pro_coins} Pro-Coins</h3>
        <p style='color:#3fb950; font-size:0.8em;'>Standard-Modelle: Unendlich ∞</p>
    </div>
    """, unsafe_allow_html=True)
    
    model_choice = st.selectbox("Modell wählen", 
                                ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro"])
    
    enable_voice = st.toggle("Live-Audio (Vorlesen)", value=True)
    
    st.divider()
    if st.button("🗑️ Chat-Verlauf löschen", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 4. CHAT-INTERFACE ---
st.title("ArslanTV AI")
st.caption("Ihr Premium KI-Assistent | Basierend auf Google-Technologie")

# Nachrichten anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Eingabe-Logik
if prompt := st.chat_input("Frage ArslanTV AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(model_choice)
            # Hier simulieren wir die KI-Antwort
            response = model.generate_content(prompt)
            full_response = response.text
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Coins abziehen bei Pro
            if "pro" in model_choice and st.session_state.pro_coins > 0:
                st.session_state.pro_coins -= 1
            
            # Sprachausgabe
            if enable_voice:
                tts = gTTS(text=full_response[:300], lang='de')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                b64 = base64.b64encode(fp.read()).decode()
                st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
                
        except Exception as e:
            if "429" in str(e):
                st.error("⏳ Limit erreicht. Bitte kurz warten (Google Free-Tier Quota).")
            else:
                st.error(f"Ein Fehler ist aufgetreten: {e}")
