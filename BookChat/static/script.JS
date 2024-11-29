// script.js

// 서버와 통신하는 함수
async function sendRequest(requestType) {
    const userId = document.getElementById('user-id').value;
    const genreInput = document.getElementById('genre-input').value;

    // 서버로 보낼 데이터
    let requestData = {
        user_id: userId,
        request_type: requestType,
        genre: genreInput
    };

    try {
        const response = await fetch('http://localhost:5555', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        displayResponse(data.message);
    } catch (error) {
        console.error('Error:', error);
        displayResponse('서버와의 통신 오류 발생!');
    }
}

// 도서 평가 기능
async function rateBook() {
    const userId = document.getElementById('user-id').value;
    const bookId = document.getElementById('book-id').value;
    const rating = document.getElementById('rating').value;

    let requestData = {
        user_id: userId,
        request_type: 'rate',
        book_id: bookId,
        rating: rating
    };

    try {
        const response = await fetch('http://localhost:5555', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        displayResponse(data.message);
    } catch (error) {
        console.error('Error:', error);
        displayResponse('서버와의 통신 오류 발생!');
    }
}

// 프로그램 종료 기능
function exitProgram() {
    displayResponse('프로그램을 종료합니다.');
}

// 서버 응답 출력 함수
function displayResponse(message) {
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = `<p>${message}</p>`;
}
