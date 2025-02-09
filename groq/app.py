import os
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Set your API key as an environment variable (ideally)
os.environ["GROQ_API_KEY"] = "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"

# Initialize the Groq client using the API key from the environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Perform a chat completion request
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama3-8b-8192",
        )
        bot_response = chat_completion.choices[0].message.content
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"response": "Error: " + str(e)})

if __name__ == "__main__":
    app.run(debug=True)
