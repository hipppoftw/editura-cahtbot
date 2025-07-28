from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os
import json

app = Flask(__name__)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Load books from file
with open("books.json", encoding="utf-8") as f:
    books = json.load(f)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    # Simple intent detection
    if is_book_question(user_message):
        return jsonify({"reply": search_books(user_message)})

    # Fallback to OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ești un asistent AI al unei edituri independente. Vorbești în limba română, răspunzi politicos și profesional. Oferi informații despre cărți, autori, tematici filosofice, sociologice, marxism, critică literară și evenimente culturale. Dacă nu știi un răspuns, încurajezi utilizatorul să trimită un mesaj prin formularul de contact. Cand un utilizator iti pune o intrebare despre tema sau continutul unei carti dai raspunsuri care apartin de filosofia critica(aceeasi tema). Raspunzi cu acelasi ton si stil ca al lui Perry Anderson. Razpunzi intr-un mod concis si eficient"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "Eroare de server. Încearcă mai târziu."}), 500

def is_book_question(msg):
    keywords = ["carte", "autor", "recomand", "titlu", "scris de", "despre"]
    return any(kw in msg.lower() for kw in keywords)

def search_books(msg):
    words = msg.lower().split()
    matches = []
    for book in books:
        title = book["titlu"].lower()
        score = sum(1 for word in words if word in title)
        if score > 0:
            matches.append((score, book))
    matches.sort(key=lambda x: -x[0])
    top = matches[:5]
    if not top:
        return "Nu am găsit nicio carte relevantă."
    return "Recomandări:\n" + "\n".join([f"• {b['titlu']} – {b['pret']} lei" for _, b in top])

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 10000))  # <- required by Render
    app.run(debug=False, host="0.0.0.0", port=port)