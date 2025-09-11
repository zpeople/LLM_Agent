from flask import Flask, request, jsonify,render_template  
from flask_cors import CORS  # 处理跨域请求

from estate_crew import RealEstateCrew

app = Flask(__name__)
CORS(app)  # 允许跨域请求，方便前端调用

# 全局存储对话状态，实际生产环境建议使用数据库或缓存
conversation_states = {}

# class RealEstateCrew:
#     """临时占位类，实际使用时替换为真实实现"""
#     def __init__(self, initial_query=None):
#         self.context = []  # 存储对话上下文
#         if initial_query:
#             self.context.append({"role": "user", "content": initial_query})
    
#     def handle_user_input(self, user_input):
#         self.context.append({"role": "user", "content": user_input})
        
#         # 简单的回复逻辑，实际应替换为真实处理逻辑
#         if "房贷" in user_input:
#             response = "房贷相关问题可以为您提供利率查询、申请条件说明等服务，请问您想了解哪方面？"
#         elif "退出" in user_input:
#             response = "感谢使用房产助手，再见！"
#         else:
#             response = f"您问的是关于'{user_input}'的问题，我会为您提供专业的房产咨询服务。"
            
#         self.context.append({"role": "assistant", "content": response})
#         return response



@app.route('/')
def index():
    return render_template('chat.html')  # 渲染templates/chat.html

# 原API接口（保持不变）
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in conversation_states:
        conversation_states[session_id] = RealEstateCrew(user_query="")
    
    crew = conversation_states[session_id]
    response = crew.handle_user_input(user_input)
    response =response if isinstance(response, str) else response.raw 

    return jsonify({
        'response': response ,
        'session_id': session_id,
        'is_quit': '退出' in user_input.lower()
    })

@app.route('/api/reset', methods=['POST'])
def reset_chat():
    data = request.json
    session_id = data.get('session_id', 'default')
    if session_id in conversation_states:
        del conversation_states[session_id]
    return jsonify({'status': 'success', 'message': '对话已重置'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)