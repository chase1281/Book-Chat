import socket
import json


def send_request(request):
    host = '127.0.0.1'
    port = 5555

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # 서버에 요청 전송
    client_socket.send(json.dumps(request).encode('utf-8'))

    # 서버로부터 응답 수신
    response = client_socket.recv(4096).decode('utf-8')
    client_socket.close()

    return json.loads(response)


def main():
    print("=== Book Chat 프로그램 ===")
    user_id = input("사용자 ID를 입력하세요: ")

    while True:
        print("\n명령어를 선택하세요:")
        print("1. 도서 추천 요청 (특정 장르)")
        print("2. 도서 추천 요청 (사용자 맞춤형)")
        print("3. 도서 평가")
        print("4. 종료")

        choice = input("선택 (1/2/3/4): ")

        if choice == '1':
            genre_request = {"request_type": "GET_GENRES"}
            response = send_request(genre_request)

            if 'genres' in response:
                print("가능한 장르 목록:")
                for genre in response['genres']:
                    print(f"- {genre}")

                selected_genre = input("추천받고 싶은 장르를 입력하세요: ")

                book_request = {"request_type": "RECOMMEND", "genre": selected_genre}
                response = send_request(book_request)

                if 'books' in response:
                    print("\n서버 응답: 추천 도서 목록")
                    for book in response['books']:
                        print(f"- ID: {book['book_id']}, 제목: {book['title']}, 저자: {book['author']}, 평가 점수: {book['avg_rating']}")
                else:
                    print("\n서버 응답:", response.get('message', '알 수 없는 오류'))

            else:
                print("\n서버 응답:", response.get('message', '알 수 없는 오류'))

        elif choice == '2':
            book_request = {"request_type": "RECOMMEND_USER", "user_id": user_id}
            response = send_request(book_request)

            if 'books' in response:
                print("\n서버 응답: 사용자 맞춤형 추천 도서 목록")
                for book in response['books']:
                    print(f"- ID: {book['book_id']}, 제목: {book['title']}, 저자: {book['author']}, 평가 점수: {book['avg_rating']}")
            else:
                print("\n서버 응답:", response.get('message', '알 수 없는 오류'))

        elif choice == '3':
            book_id = input("평가할 도서의 ID를 입력하세요: ")
            rating = input("도서에 대한 평가 점수 (1~5)를 입력하세요: ")

            rate_request = {
                "request_type": "RATE_BOOK",
                "book_id": book_id,
                "user_id": user_id,
                "rating": int(rating)
            }
            response = send_request(rate_request)

            print("\n서버 응답:", response.get('message', '알 수 없는 오류'))

        elif choice == '4':
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 선택입니다. 다시 시도하세요.")


if __name__ == "__main__":
    main()
