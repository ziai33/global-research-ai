from http.server import BaseHTTPRequestHandler
import json
import os
import anthropic

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            topic = data.get('topic', '')
            industry = data.get('industry', '')
            region = data.get('region', '')

            if not topic:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': '请提供调研主题'}).encode('utf-8'))
                return

            api_key = os.environ.get('OPEN_API_KEY')
            if not api_key:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'API Key 未配置'}).encode('utf-8'))
                return

            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""你是一位顶级战略咨询顾问，拥有麦肯锡、波士顿咨询集团的专业背景。
请针对以下主题生成一份专业的四维度战略调研报告：

调研主题：{topic}
行业领域：{industry if industry else '综合'}
地区范围：{region if region else '全球'}

请严格按照以下四个维度进行深度分析，每个维度需要详细、专业、有数据支撑：

## 维度一：市场格局与竞争态势
- 市场规模与增长趋势
- 主要竞争者分析
- 市场集中度与竞争强度
- 行业壁垒与护城河

## 维度二：宏观环境与政策驱动
- 政策法规环境分析（PEST框架）
- 监管趋势与合规要求
- 地缘政治与经济周期影响
- 技术变革与数字化转型

## 维度三：价值链与商业模式创新
- 产业价值链结构分析
- 核心商业模式对比
- 盈利模式与变现路径
- 创新机会与颠覆性风险

## 维度四：战略建议与行动路径
- 关键成功因素（KSF）
- 短期（0-12个月）优先行动
- 中期（1-3年）战略布局
- 长期（3-5年）愿景规划
- 风险预警与应对措施

请确保报告：
1. 语言专业、逻辑严密
2. 包含具体数据和案例
3. 提供可操作的战略建议
4. 格式清晰，层次分明

请用中文撰写完整报告。"""

            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            report_content = message.content[0].text

            response_data = {
                'success': True,
                'topic': topic,
                'industry': industry,
                'region': region,
                'report': report_content,
                'model': message.model,
                'usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                }
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

        except anthropic.APIConnectionError:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'API 连接失败，请检查网络'}).encode('utf-8'))

        except anthropic.RateLimitError:
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'API 请求频率超限，请稍后重试'}).encode('utf-8'))

        except anthropic.APIStatusError as e:
            self.send_response(e.status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'API 错误: {e.message}'}).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'服务器内部错误: {str(e)}'}).encode('utf-8'))
