from flask import Flask, request, jsonify, render_template
import os
from groq import Groq

app = Flask(__name__)

# Set your API key as an environment variable (ideally)
os.environ["GROQ_API_KEY"] = "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"

# Initialize the Groq client using the API key from the environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Get form data
        data = request.json

        # Create a prompt for Groq API
        prompt = f"Based on the following details, recommend a diet plan: {json.dumps(data)}"

        # Perform a chat completion request
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        bot_response = chat_completion.choices[0].message.content
        return jsonify({"status": "success", "recommendation": bot_response})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)