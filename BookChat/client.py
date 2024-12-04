import requests

def send_genre_request(user_id, genre):
    response = requests.post('http://127.0.0.1:5000/recommend', json={
        'user_id': user_id,
        'genre': genre
    })
    return response.json()

def send_book_rating(user_id, book_id, rating):
    response = requests.post('http://127.0.0.1:5000/rate_book', json={
        'user_id': user_id,
        'book_id': book_id,
        'rating': rating
    })
    return response.json()

# 예시 사용법
user_id = "kmj"  # 사용자 ID
genre = "fiction"  # 장르
books_response = send_genre_request(user_id, genre)
print(books_response)

book_id = 1  # 평가할 도서의 ID
rating = 4.5  # 평가 점수
rating_response = send_book_rating(user_id, book_id, rating)
print(rating_response)
