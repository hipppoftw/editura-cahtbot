from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow all origins by default

# Load OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load books data
with open("books.json", encoding="utf-8") as f:
    books = json.load(f)

@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if is_book_question(user_message):
        return jsonify({"reply": search_books(user_message)})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ești un asistent AI al unei edituri independente. Vorbești în limba română..."
                },
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
    port = int(os.environ.get("PORT", 10000))  # Render requires binding to this port
    app.run(debug=False, host="0.0.0.0", port=port)
