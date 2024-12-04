from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3

# Flask 및 SocketIO 초기화
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


# 데이터베이스 연결 함수
def connect_database():
    return sqlite3.connect('book_chat.db')


# 장르 목록 가져오기
def get_genre_list():
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT genre FROM books')
        genres = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching genres: {e}")
        return []
    finally:
        conn.close()
    return genres


# 특정 장르 추천
def recommend_books_by_genre(selected_genre, user_id):
    try:
        conn = connect_database()
        cursor = conn.cursor()
        # 장르별로 도서를 추천하고, 평가 점수의 평균을 계산하여 내림차순으로 정렬
        cursor.execute('''
            SELECT b.id, b.title, b.author, 
                   IFNULL(AVG(br.rating), 0) AS avg_rating
            FROM books b
            LEFT JOIN book_ratings br ON b.id = br.book_id AND br.user_id = ?
            WHERE b.genre = ?
            GROUP BY b.id, b.title, b.author
            ORDER BY avg_rating DESC
        ''', (user_id, selected_genre))
        books = cursor.fetchall()
    except Exception as e:
        print(f"Error recommending books for genre {selected_genre}: {e}")
        return []
    finally:
        conn.close()

    if not books:
        return None

    # 도서 리스트 반환 (id, title, author, avg_rating 포함)
    return [{"book_id": book[0], "title": book[1], "author": book[2], "avg_rating": book[3]} for book in books]


# 사용자가 장르를 선택했을 때 선택 횟수 저장
def save_user_genre_request(user_id, genre):
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO user_requests (user_id, genre, request_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, genre) 
            DO UPDATE SET request_count = request_count + 1
        ''', (user_id, genre))
        conn.commit()
    except Exception as e:
        print(f"Error saving user genre request for user {user_id} and genre {genre}: {e}")
    finally:
        conn.close()


# 도서 평가 저장
def save_book_rating(user_id, book_id, rating):
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO book_ratings (user_id, book_id, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, book_id) 
            DO UPDATE SET rating = ?
        ''', (user_id, book_id, rating, rating))
        conn.commit()
    except Exception as e:
        print(f"Error saving book rating for user {user_id}, book {book_id}: {e}")
    finally:
        conn.close()


# 사용자 맞춤형 장르 추천
def recommend_custom_genre(user_id):
    try:
        conn = connect_database()
        cursor = conn.cursor()
        # 각 장르에 대한 요청 횟수와 평균 평가 점수 계산
        cursor.execute('''
            SELECT ur.genre, SUM(ur.request_count) AS total_requests, 
                   IFNULL(AVG(br.rating), 0) AS avg_rating
            FROM user_requests ur
            LEFT JOIN books b ON ur.genre = b.genre
            LEFT JOIN book_ratings br ON b.id = br.book_id AND br.user_id = ur.user_id
            WHERE ur.user_id = ?
            GROUP BY ur.genre
            ORDER BY total_requests DESC, avg_rating DESC
            LIMIT 1;
        ''', (user_id,))
        genre_data = cursor.fetchone()
    except Exception as e:
        print(f"Error recommending custom genre for user {user_id}: {e}")
        return {"status": "error", "message": "장르 추천 정보가 없습니다."}
    finally:
        conn.close()

    if genre_data:
        selected_genre = genre_data[0]
        books = recommend_books_by_genre(selected_genre, user_id)
        if books:
            return {"status": "success", "genre": selected_genre, "data": books, "request_type": "RECOMMEND_GENRE"}
    return {"status": "error", "message": "장르 추천 정보가 없습니다."}


# 새로운 사용자 초기화
def initialize_user(user_id):
    try:
        conn = connect_database()
        cursor = conn.cursor()
        # 새로운 사용자의 평가 기록을 0으로 초기화
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id)
            VALUES (?)
        ''', (user_id,))

        cursor.execute('''
            INSERT OR IGNORE INTO book_ratings (user_id, book_id, rating)
            SELECT ?, id, 0 FROM books
        ''', (user_id,))

        conn.commit()
    except Exception as e:
        print(f"Error initializing user {user_id}: {e}")
    finally:
        conn.close()


# 요청 처리 함수
def handle_request(data):
    request_type = data.get("request_type")
    user_id = data.get("user_id")
    print(f"Handling request of type: {request_type} for user: {user_id}")

    if request_type == "INITIALIZE_USER" and user_id:
        initialize_user(user_id)
        return {"status": "success", "message": f"사용자 {user_id} 초기화 완료."}

    elif request_type == "GET_GENRES":
        genres = get_genre_list()
        return {"status": "success", "data": genres, "request_type": "GET_GENRES"}

    elif request_type == "RECOMMEND" and "genre" in data:
        selected_genre = data.get("genre")
        save_user_genre_request(user_id, selected_genre)
        books = recommend_books_by_genre(selected_genre, user_id)
        if books:
            return {"status": "success", "data": books, "request_type": "RECOMMEND"}
        else:
            return {"status": "error", "message": f"해당 장르 [{selected_genre}]의 추천 도서가 없습니다."}

    elif request_type == "RATE_BOOK" and "book_id" in data:
        book_id = data.get("book_id")
        rating = data.get("rating")
        save_book_rating(user_id, book_id, rating)
        return {"status": "success", "message": "도서 평가가 저장되었습니다.", "book_id": book_id, "rating": rating}

    elif request_type == "RECOMMEND_CUSTOM_GENRE" and user_id:
        return recommend_custom_genre(user_id)

    else:
        return {"status": "error", "message": "알 수 없는 요청입니다."}


# HTML 렌더링
@app.route('/')
def index():
    return render_template('index.html')


# WebSocket 메시지 처리
@socketio.on('message')
def handle_message(data):
    print(f"Received data: {data}")
    response = handle_request(data)
    emit('response', response, broadcast=False)


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
