import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# 自动读取环境变量，解决路径拼接问题
api_key = os.environ.get('OPENAI_API_KEY', 'sk-of-sYpNFVAtkFCMztuRykwZRGKJbVGPsmYMnVSNCdcztcXhZiauECeBYXUosTsQcVCU')
base_url = os.environ.get('OPENAI_API_BASE', 'https://api.ofox.ai/v1')

# 初始化标准客户端
client = openai.OpenAI(api_key=api_key, base_url=base_url)

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        topic = data.get('topic', '中国零食市场')
        
        # 强制使用最通用的 gpt-4o 模型名
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位资深的战略咨询顾问。"},
                {"role": "user", "content": f"请针对主题【{topic}】生成一份详细的战略调研报告。"}
            ]
        )
        return jsonify({'report': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': f'连接失败原因: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
