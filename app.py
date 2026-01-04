import streamlit as st
import google.generativeai as genai

# 1. Design & Branding
st.set_page_config(page_title="ArslanTV AI")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #1A1D23; }
    </style>
    """, unsafe_allow_html=True)

st.title("ArslanTV AI")
st.markdown("Ihr Profi-KI-Assistent.")

# 2. API-Key sicher laden
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte den GOOGLE_API_KEY in den Streamlit-Secrets hinterlegen.")
    st.stop()

# 3. Chat-Historie
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. KI Logik (Der ultimative Fix)
if prompt := st.chat_input("Wie kann ich Ihnen helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Wir probieren erst den modernsten Namen
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
        except:
            # Falls das scheitert, nehmen wir den absoluten Pfad
            model = genai.GenerativeModel('models/gemini-pro')
            response = model.generate_content(prompt)
        
        answer = response.text
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
            
    except Exception as e:
        st.error(f"Hinweis: Die KI startet gerade neu. Bitte versuchen Sie es in 10 Sekunden nochmal. (Technischer Code: {e})")

