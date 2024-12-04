import socket
import json
import base64
import hashlib


def handle_request(data):
    """ 클라이언트로부터 받은 데이터를 처리하는 함수 """
    print(f"서버에서 받은 데이터: {data}")

    # 예시 처리: 요청에 맞게 데이터를 응답
    if data['request_type'] == 'GET_GENRES':
        return {
            "status": "success",
            "data": ["Fiction", "Romance", "Fantasy", "Mystery", "Horror"]  # 장르 목록 예시
        }
    elif data['request_type'] == 'RECOMMEND':
        return {
            "status": "success",
            "data": f"추천 도서 목록: {data['genre']}"
        }
    elif data['request_type'] == 'RATE_BOOK':
        return {
            "status": "success",
            "message": f"도서 {data['book_id']}에 {data['rating']}점 평가 완료"
        }
    else:
        return {"status": "error", "message": "알 수 없는 요청"}


def generate_accept_key(client_key):
    """ WebSocket 핸드쉐이크에서 Sec-WebSocket-Accept 키를 생성하는 함수 """
    magic_string = "258EAFA5-E914-47DA-95CA-C5B6D2D0FB9D"
    sha1_hash = hashlib.sha1((client_key + magic_string).encode('utf-8')).digest()
    return base64.b64encode(sha1_hash).decode('utf-8')


def start_server():
    host = '127.0.0.1'
    port = 5555

    # 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"서버가 {port} 포트에서 시작되었습니다. 클라이언트를 기다립니다...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"{addr}에서 연결되었습니다.")

        # HTTP 요청(웹소켓 핸드쉐이크)을 처리
        handshake = client_socket.recv(1024).decode('utf-8')
        print(f"클라이언트로부터 받은 핸드쉐이크: {handshake}")

        # WebSocket 핸드쉐이크 응답 보내기
        client_key = handshake.split("Sec-WebSocket-Key: ")[1].split("\r\n")[0]
        accept_key = generate_accept_key(client_key)

        headers = "HTTP/1.1 101 Switching Protocols\r\n"
        headers += "Upgrade: websocket\r\n"
        headers += "Connection: Upgrade\r\n"
        headers += f"Sec-WebSocket-Accept: {accept_key}\r\n"
        headers += "\r\n\r\n"
        client_socket.send(headers.encode('utf-8'))

        # WebSocket 메시지 수신 및 처리
        while True:
            try:
                # WebSocket 메시지를 받기
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break  # 연결이 끊어졌으면 종료

                print(f"서버에서 받은 메시지: {data}")

                # 받은 메시지가 JSON 형식인 경우 파싱
                try:
                    if data:
                        request = json.loads(data)  # JSON 형식으로 파싱
                        response = handle_request(request)

                        # WebSocket 응답으로 처리된 데이터 전송
                        response_data = json.dumps(response)
                        client_socket.send(response_data.encode('utf-8'))

                except json.JSONDecodeError:
                    print("잘못된 JSON 데이터 수신")
                    break

            except Exception as e:
                print(f"오류 발생: {e}")
                break

        # 클라이언트와의 연결 종료
        client_socket.close()


# 서버 시작
start_server()
