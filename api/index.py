import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
    base_url=os.environ.get('OPENAI_API_BASE', 'https://api.ofox.ai/v1')
)

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        topic = data.get('topic')
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"请生成关于【{topic}】的战略调研报告"}]
        )
        return jsonify({'report': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)})

# Vercel 需要
def handler(request):
    return app(request)
