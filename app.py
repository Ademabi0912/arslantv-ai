import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ArslanTV Diagnose", page_icon="🔍")
st.title("🔍 ArslanTV System-Check")

# 1. Key laden
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("Key fehlt in den Secrets!")
    st.stop()

st.write("Verbinde mit Google Servern...")

# 2. Diagnose starten
try:
    # Wir fragen Google direkt: "Was darf ich nutzen?"
    found_models = []
    for m in genai.list_models():
        # Wir filtern nur Modelle, die auch Text generieren können
        if 'generateContent' in m.supported_generation_methods:
            found_models.append(m.name)

    if found_models:
        st.success(f"Erfolg! {len(found_models)} Modelle gefunden:")
        # Hier wird die GENAUE Liste angezeigt
        st.code("\n".join(found_models))
        st.warning("👉 Bitte mache einen Screenshot von dieser Liste und zeige ihn mir!")
    else:
        st.error("Verbindung steht, aber Google sagt: 'Keine Modelle für diesen Key verfügbar'.")
        st.info("Das passiert oft, wenn im Google Cloud Projekt die 'Generative Language API' nicht aktiviert ist.")

except Exception as e:
    st.error(f"Verbindungsfehler: {e}")
