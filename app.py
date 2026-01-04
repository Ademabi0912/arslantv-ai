import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="ArslanTV AI", page_icon="🤖")
st.title("🤖 ArslanTV AI")
st.markdown("Ihr Profi-KI-Assistent für alle Antworten.")

# API-Key Check
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please add the GOOGLE_API_KEY to Streamlit Secrets.")

# System Personality
SYSTEM_PROMPT = """
Du bist ArslanTV AI, ein hochprofessioneller digitaler Assistent.
Deine Antworten sind immer in korrektem, gehobenem Deutsch.
Du achtest auf Grammatik und Rechtschreibung.
Dein Tonfall ist höflich, sachlich und lösungsorientiert.
"""

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Wie kann ich Ihnen helfen?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    try:
        model = genai.GenerativeModel(
           model_name="gemini-pro",
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Fehler: {e}")




