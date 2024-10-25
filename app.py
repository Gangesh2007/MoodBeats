from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load the saved model and vectorizer
model = joblib.load('chatbot_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

responses = {
    "happy": "Yass! 🎉 You're vibing! Let's get those good tunes rolling! 🎶",
    "sad": "Aww, that sucks. 😢 Let’s find some chill beats to lift you up. 💔",
    "excited": "Lit! 🔥 Let’s keep that energy going with some hype tracks! 🚀",
    "greeting": "Hey there! 👋 What's on your mind?",
    "confident": "That's the spirit! 💪 You've got this! Let's find some powerful anthems for you. 🌟",
    "breakup": "Breakups are tough. 💔 Let’s find some soulful tunes to help you heal. 💿"
}

def get_response(user_input):
    input_vectorized = vectorizer.transform([user_input])  # Vectorize the user input
    predicted_intent = model.predict(input_vectorized)[0]  # Predict intent
    return responses.get(predicted_intent, "It’s AI mind 😎 Just vibing here!")

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("input")
    bot_response = get_response(user_input)
    return jsonify({"reply": bot_response})

@app.route('/')
def home():
    return jsonify({'message': 'Server is running!'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
