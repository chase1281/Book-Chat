import sqlite3
import socket
import json

# 데이터베이스 연결 함수
def connect_database():
    return sqlite3.connect('book_chat.db')


# 장르 목록 가져오기
def get_genre_list():
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute('''SELECT DISTINCT genre FROM books''')
    genres = [row[0] for row in cursor.fetchall()]

    conn.close()
    return genres


# 책 평가 저장 함수
def save_book_rating(book_id, user_id, rating):
    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO book_ratings (book_id, user_id, rating) VALUES (?, ?, ?)''',
                       (book_id, user_id, rating))
        conn.commit()
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        return False
    finally:
        conn.close()
    return True


# 특정 장르에 대한 도서 추천 함수
def recommend_books_by_genre(selected_genre):
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT b.id, b.title, b.author, IFNULL(AVG(br.rating), 0) AS avg_rating
    FROM books b
    LEFT JOIN book_ratings br ON b.id = br.book_id
    WHERE b.genre = ?
    GROUP BY b.id, b.title, b.author
    ORDER BY avg_rating DESC
    ''', (selected_genre,))

    recommended_books = cursor.fetchall()
    conn.close()

    return recommended_books


# 사용자 맞춤형 추천 함수
def recommend_books_for_user(user_id):
    conn = connect_database()
    cursor = conn.cursor()

    # 사용자가 평가한 책을 기준으로 추천
    cursor.execute('''
    SELECT DISTINCT b.id, b.title, b.author, IFNULL(AVG(br.rating), 0) AS avg_rating
    FROM books b
    JOIN book_ratings br ON b.id = br.book_id
    WHERE br.user_id = ?
    GROUP BY b.id
    ORDER BY avg_rating DESC
    LIMIT 5
    ''', (user_id,))

    recommended_books = cursor.fetchall()
    conn.close()

    return recommended_books


# 요청 처리 함수
def handle_request(request):
    request_type = request.get("request_type")

    if request_type == "GET_GENRES":
        genres = get_genre_list()
        return {"genres": genres} if genres else {"message": "추천 가능한 장르가 없습니다."}

    elif request_type == "RECOMMEND" and "genre" in request:
        selected_genre = request.get("genre")
        books = recommend_books_by_genre(selected_genre)
        if books:
            book_list = [{"book_id": book[0], "title": book[1], "author": book[2], "avg_rating": book[3]} for book in books]
            return {"books": book_list}
        else:
            return {"message": f"해당 장르 [{selected_genre}]의 추천 도서가 없습니다."}

    elif request_type == "RATE_BOOK" and all(key in request for key in ["book_id", "user_id", "rating"]):
        book_id = request["book_id"]
        user_id = request["user_id"]
        rating = request["rating"]
        if save_book_rating(book_id, user_id, rating):
            return {"message": f"도서 ID {book_id}에 대한 평가가 {rating}점으로 저장되었습니다."}
        else:
            return {"message": "도서 평가를 저장하는 데 실패했습니다."}

    elif request_type == "RECOMMEND_USER" and "user_id" in request:
        user_id = request["user_id"]
        books = recommend_books_for_user(user_id)
        if books:
            book_list = [{"book_id": book[0], "title": book[1], "author": book[2], "avg_rating": book[3]} for book in books]
            return {"books": book_list}
        else:
            return {"message": "사용자 맞춤형 추천 도서를 찾을 수 없습니다."}

    else:
        return {"message": "알 수 없는 요청입니다."}


# 서버 초기화 및 클라이언트 요청 처리
def start_server():
    host = '127.0.0.1'
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"서버가 {port} 포트에서 시작되었습니다. 클라이언트를 기다립니다...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"{addr}에서 연결되었습니다.")

        try:
            data = client_socket.recv(1024).decode('utf-8')
            request = json.loads(data)

            response = handle_request(request)

            client_socket.send(json.dumps(response).encode('utf-8'))
        except json.JSONDecodeError:
            print("잘못된 JSON 데이터 수신")
        except Exception as e:
            print(f"오류 발생: {e}")
        finally:
            client_socket.close()


# 서버 실행
start_server()
