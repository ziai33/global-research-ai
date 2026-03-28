import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# 强制初始化
api_key = os.environ.get('OPENAI_API_KEY', 'sk-of-sYpNFVAtkFCMztuRykwZRGKJbVGPsmYMnVSNCdcztcXhZiauECeBYXUosTsQcVCU')
base_url = os.environ.get('OPENAI_API_BASE', 'https://api.ofox.ai/v1')
client = openai.OpenAI(api_key=api_key, base_url=base_url)

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        topic = data.get('topic', '中国零食市场')
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"请针对【{topic}】生成调研报告"}]
        )
        return jsonify({'report': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
