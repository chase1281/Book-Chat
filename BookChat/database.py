import sqlite3

# 데이터베이스 연결 함수
def connect_database():
    return sqlite3.connect('book_chat.db')

# 장르 요청 횟수 저장
def save_genre_request(user_id, genre):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_requests (user_id, genre, request_count)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, genre)
        DO UPDATE SET request_count = request_count + 1
    ''', (user_id, genre))
    conn.commit()
    conn.close()

# 도서 평가 저장
def save_book_rating(user_id, book_id, rating):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO book_ratings (user_id, book_id, rating)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, book_id)
        DO UPDATE SET rating = ?
    ''', (user_id, book_id, rating, rating))
    conn.commit()
    conn.close()

# 장르별 도서 추천 가져오기
def get_books_by_genre(genre):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.title, b.author, IFNULL(AVG(br.rating), 0) AS avg_rating
        FROM books b
        LEFT JOIN book_ratings br ON b.id = br.book_id
        WHERE b.genre = ?
        GROUP BY b.id, b.title, b.author
        ORDER BY avg_rating DESC
    ''', (genre,))
    books = cursor.fetchall()
    conn.close()

    return [{"book_id": book[0], "title": book[1], "author": book[2], "avg_rating": book[3]} for book in books]
