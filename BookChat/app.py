from flask import Flask, render_template, request, jsonify
import sqlite3
import logging

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE = 'book_chat.db'


def connect_database():
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except sqlite3.Error as e:
        logging.error(f"데이터베이스 연결 실패: {e}")
        return None


# 기본 페이지
@app.route('/')
def index():
    return render_template('index.html')


# 장르 목록 가져오기
@app.route('/api/genres', methods=['GET'])
def get_genres():
    conn = connect_database()
    if not conn:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT genre FROM books')
        genres = [row[0] for row in cursor.fetchall()]
        return jsonify({"genres": genres})
    except sqlite3.Error as e:
        logging.error(f"장르 조회 실패: {e}")
        return jsonify({"error": "장르 조회 실패"}), 500
    finally:
        conn.close()


# 책 추천 API
@app.route('/api/recommend', methods=['POST'])
def recommend_books():
    data = request.get_json()

    if not data or "genre" not in data:
        return jsonify({"error": "요청 데이터가 올바르지 않습니다."}), 400

    selected_genre = data['genre']
    conn = connect_database()
    if not conn:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.id, b.title, b.author, IFNULL(AVG(br.rating), 0) AS avg_rating
            FROM books b
            LEFT JOIN book_ratings br ON b.id = br.book_id
            WHERE b.genre = ?
            GROUP BY b.id
            ORDER BY avg_rating DESC
        ''', (selected_genre,))
        books = cursor.fetchall()

        if not books:
            return jsonify({"message": f"해당 장르 [{selected_genre}]에 추천 도서가 없습니다."})

        return jsonify({
            "books": [
                {"id": book[0], "title": book[1], "author": book[2], "avg_rating": book[3]} for book in books
            ]
        })
    except sqlite3.Error as e:
        logging.error(f"추천 도서 조회 실패: {e}")
        return jsonify({"error": "추천 도서 조회 실패"}), 500
    finally:
        conn.close()


# 책 평가 저장 API
@app.route('/api/rate', methods=['POST'])
def rate_book():
    data = request.get_json()

    required_fields = ["book_id", "user_id", "rating"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "요청 데이터가 올바르지 않습니다."}), 400

    book_id = data['book_id']
    user_id = data['user_id']
    rating = data['rating']

    conn = connect_database()
    if not conn:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO book_ratings (book_id, user_id, rating)
            VALUES (?, ?, ?)
        ''', (book_id, user_id, rating))
        conn.commit()
        return jsonify({"message": "도서 평가가 저장되었습니다."})
    except sqlite3.Error as e:
        logging.error(f"도서 평가 저장 실패: {e}")
        return jsonify({"error": "도서 평가 저장 실패"}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
