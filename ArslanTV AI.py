# ArslanTV AI – Chatbot, der praktisch jede Frage beantworten kann
# Nutzt OpenAI API (ähnlich wie Gemini, legal und sicher)

import openai
import os

# API-Key aus Environment Variable holen
openai.api_key = os.getenv("OPENAI_API_KEY")

def arslantv_ai_chat(prompt, max_tokens=300):
    """
    Funktion: ArslanTV AI antwortet auf jede Frage
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # leistungsstarkes Modell
            prompt=f"Du bist ArslanTV AI, eine intelligente KI. Beantworte jede Frage präzise und freundlich:\n{prompt}",
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Fehler: {e}"

def main():
    print("ArslanTV AI gestartet! (Tippe 'exit' zum Beenden)")
    while True:
        user_input = input("Du: ")
        if user_input.lower() == "exit":
            print("ArslanTV AI: Bis bald!")
            break
        answer = arslantv_ai_chat(user_input)
        print(f"ArslanTV AI: {answer}")

if __name__ == "__main__":
    main()
