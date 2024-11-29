from flask import Flask, render_template, request, jsonify
import sqlite3  # 데이터베이스 연결을 위한 예시

app = Flask(__name__)

# 기본 페이지
@app.route('/')
def index():
    return render_template('index.html')  # index.html 파일을 렌더링

# Book Chat 기능을 위한 예시 API 엔드포인트
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']  # 사용자가 보낸 메시지
    # 이곳에 Book Chat 기능을 처리하는 코드 추가
    response = get_book_recommendation(user_input)  # 예시 함수
    return jsonify(response)

def get_book_recommendation(user_input):
    # 실제 책 추천을 처리하는 코드
    return {"book": "추천 책 제목", "author": "책 저자"}

if __name__ == '__main__':
    app.run(debug=True)
