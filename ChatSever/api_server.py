from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from ollama import chat

app = Flask(__name__)
CORS(app) # Cho phép Cross-Origin Resource Sharing cho tất cả các route

# Khởi tạo list để lưu lịch sử tin nhắn
# Lưu ý: Trong môi trường production, bạn sẽ cần một cách lưu trữ lịch sử chat bền vững hơn
# (ví dụ: database) thay vì biến toàn cục, vì biến này sẽ reset khi server khởi động lại
# hoặc khi có nhiều người dùng đồng thời.
messages = []

# Định nghĩa tính cách cho chatbot (chỉ cần thêm 1 lần khi server khởi động)
personality = "Bạn là một cô gái, tên là Ruby, tính cách thân thiện, cởi mở. Luôn nói tiếng Việt và yêu thích Việt Nam"
messages.append({'role': 'system', 'content': f"Bạn là một chatbot có tính cách {personality}."})

@app.route('/chat', methods=['POST'])
def chatbot_endpoint():
    global messages # Cho phép sửa đổi biến messages toàn cục

    # Lấy dữ liệu tin nhắn từ yêu cầu POST
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    # Thêm tin nhắn của người dùng vào lịch sử chat
    messages.append({'role': 'user', 'content': user_message})

    try:
        # Gọi API của Ollama để lấy phản hồi từ model
        response = chat(
            model='gemma3:4b',
            messages=messages
        )
        assistant_response_content = response.message.content

        # Thêm phản hồi của chatbot vào lịch sử chat
        messages.append({'role': 'assistant', 'content': assistant_response_content})

        # Trả về phản hồi cho frontend dưới dạng JSON
        return jsonify({"response": assistant_response_content})

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return jsonify({"error": "Failed to get response from chatbot"}), 500

if __name__ == '__main__':
    # Chạy Flask app trên cổng 5000
    # host='0.0.0.0' cho phép truy cập từ các thiết bị khác trong mạng cục bộ (nếu cần)
    app.run(debug=True, port=5000, host='0.0.0.0')