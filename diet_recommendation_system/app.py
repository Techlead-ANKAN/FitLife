from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Groq API endpoint and key
GROQ_API_URL = "https://api.groq.com/recommend"
GROQ_API_KEY = "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"

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # Get form data
        data = request.json

        # Send data to Groq API for diet recommendation
        prompt = f"Based on the following details, recommend a diet plan: {json.dumps(data)}"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(GROQ_API_URL, json={"prompt": prompt}, headers=headers)
        recommendation = response.json().get("recommendation", "No recommendation available.")

        return jsonify({"status": "success", "recommendation": recommendation})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)