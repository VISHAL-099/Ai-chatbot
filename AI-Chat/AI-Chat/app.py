from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

app = Flask(__name__)

def generate_response(prompt):
    """Generate response from the AI model."""
    try:
        completion = client.chat.completions.create(
            model="nvidia/nemotron-4-mini-hindi-4b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
            stream=False
        )
        # Access response content correctly
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
    
@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    """Handle AJAX request for AI response."""
    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({"error": "No input provided!"}), 400
    response = generate_response(user_input)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
