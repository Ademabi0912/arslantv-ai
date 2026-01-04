import streamlit as st
import google.generativeai as genai

# Konfiguration der Webseite
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")
st.title("🤖 ArslanTV AI")
st.markdown("Ihr professioneller KI-Assistent für alle Anfragen.")

# API-Key Sicherung (Wichtig für das Deployment)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Bitte hinterlegen Sie den GOOGLE_API_KEY in den Streamlit Secrets.")

# Definition der professionellen Persönlichkeit
SYSTEM_PROMPT = """
Du bist ArslanTV AI, ein hochprofessioneller digitaler Assistent. 
Deine Antworten sind stets in korrektem, gehobenem Deutsch verfasst. 
Du achtest strikt auf Grammatik und Rechtschreibung. 
Dein Tonfall ist höflich, sachlich und lösungsorientiert. 
Vermeide Umgangssprache und bleibe immer seriös.
"""

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Anzeige des Chat-Verlaufs
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Eingabe des Nutzers
if prompt := st.chat_input("Wie kann ich Ihnen heute behilflich sein?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.session_state.chat_session.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
