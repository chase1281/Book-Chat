document.addEventListener("DOMContentLoaded", () => { // 각 섹션과 주요 HTML 요소들을 정의
    const loginSection = document.getElementById("login-section");
    const menuSection = document.getElementById("menu-section");
    const outputSection = document.getElementById("output-section");
    const genreRequestSection = document.getElementById("genre-request-section");
    const userIdInput = document.getElementById("user-id");
    const outputDiv = document.getElementById("output");
    const genreListSection = document.getElementById("genre-list");

    // 사용자 ID와 선택된 장르를 저장할 변수들
    let userId = "";
    let selectedGenre = "";
    let socket = io.connect('http://127.0.0.1:5000'); // Flask-SocketIO 서버에 연결

    // 특정 섹션만 표시하고 나머지 섹션은 숨기는 함수
    const showSection = (section) => {
        loginSection.classList.add("hidden");
        menuSection.classList.add("hidden");
        outputSection.classList.add("hidden");
        genreRequestSection.classList.add("hidden");
        section.classList.remove("hidden");
    };

    // 서버에 연결하고 연결 상태를 관리하는 함수
    const connectToServer = () => {
        socket.on('connect', () => {
            console.log("WebSocket 연결 성공");
        });

        socket.on('disconnect', () => {
            console.log("서버와 연결이 끊어졌습니다.");
            alert("서버 연결이 끊어졌습니다.");
        });

        socket.on('response', (response) => {
            console.log("서버로부터 응답 수신: ", response);
            handleResponse(response);
        });
    };

    // 서버로 요청을 전송하는 함수
    const sendRequest = (requestData) => {
        console.log("서버로 요청 전송: ", requestData);
        if (socket.connected) {
            socket.emit("message", requestData);
        } else {
            alert("서버와의 연결이 끊어졌습니다. 새로고침 해주세요.");
        }
    };

    // 서버 응답을 처리하는 함수
    const handleResponse = (response) => {
        console.log("응답 처리 중: ", response);  // 응답 처리 로그 추가
        if (response.status === "success") {
            if (response.request_type === "GET_GENRES") {
                console.log("장르 목록 응답 처리");
                genreListSection.innerHTML = "";
                response.data.forEach((genre) => {
                    const genreButton = document.createElement("button");
                    genreButton.textContent = genre;
                    genreButton.classList.add("genre-btn");
                    genreButton.addEventListener("click", () => {
                        selectedGenre = genre;
                        console.log(`장르 선택됨: ${selectedGenre}`);
                        sendRequest({ request_type: "RECOMMEND", genre: genre, user_id: userId });
                    });
                    genreListSection.appendChild(genreButton);
                });
                showSection(genreRequestSection);
            } else if (response.request_type === "RECOMMEND") {
                console.log("추천 도서 목록 응답 처리");
                if (response.data && response.data.length > 0) {
                    outputDiv.innerHTML = "<h3>추천 도서:</h3><ul>";
                    response.data.forEach((book) => {
                        const bookItem = document.createElement("li");
                        bookItem.innerHTML = `${book.title} - ${book.author} (점수: ${book.avg_rating}) 
                                              <button class="rate-btn" data-book-id="${book.book_id}">평가하기</button>`;
                        outputDiv.appendChild(bookItem);
                    });
                    outputDiv.innerHTML += "</ul>";
                    showSection(outputSection);

                    // 도서 평가 버튼 클릭 이벤트
                    document.querySelectorAll(".rate-btn").forEach((button) => {
                        button.addEventListener("click", () => {
                            const bookId = button.getAttribute("data-book-id");
                            let rating = prompt("도서에 대한 평가 점수 (0~5 사이의 소수점 한자리로 입력하세요):");
                            if (rating === null) {
                                return; // 사용자가 입력을 취소한 경우
                            } else if (isValidRating(rating)) {
                                sendRequest({
                                    request_type: "RATE_BOOK",
                                    user_id: userId,
                                    book_id: parseInt(bookId),
                                    rating: parseFloat(rating),
                                });
                            } else {
                                alert("잘못된 입력입니다. 0부터 5 사이의 숫자 또는 소수점 한 자리를 입력해주세요.");
                            }
                        });
                    });
                }
            } else if (response.request_type === "RATE_BOOK") {
                console.log("도서 평가 응답 처리");
                alert(response.message);
                updateBookRating(response.book_id, response.rating);
                updateBookListSorted();
            } else if (response.request_type === "RECOMMEND_GENRE") {
                console.log("사용자 맞춤형 장르 추천 응답 처리");
                const genre = response.genre;
                const books = response.data;

                outputDiv.innerHTML = `<h3>추천 장르: ${genre}</h3><ul>`;
                books.forEach(book => {
                    outputDiv.innerHTML += `<li>${book.title} - ${book.author} (평균 점수: ${book.avg_rating})</li>`;
                });
                outputDiv.innerHTML += "</ul>";
                showSection(outputSection);
            }
        } else {
            alert(response.message);
        }
    };

    // 도서 평가 점수를 업데이트하는 함수
    const updateBookRating = (bookId, rating) => {
        const bookItems = document.querySelectorAll("li");
        bookItems.forEach((item) => {
            const bookButton = item.querySelector("button");
            if (bookButton && bookButton.getAttribute("data-book-id") === String(bookId)) {
                item.innerHTML = item.innerHTML.replace(/점수: \d+(\.\d+)?/, `점수: ${rating}`);
            }
        });
    };

    // 도서 목록을 평가 점수에 따라 정렬하는 함수
    const updateBookListSorted = () => {
        const bookItems = document.querySelectorAll("li");
        let updatedItems = Array.from(bookItems);

        updatedItems.sort((a, b) => {
            const ratingA = parseFloat(a.innerHTML.split("점수: ")[1]);
            const ratingB = parseFloat(b.innerHTML.split("점수: ")[1]);
            return ratingB - ratingA;
        });

        outputDiv.innerHTML = "<h3>추천 도서:</h3><ul>";
        updatedItems.forEach((item) => {
            outputDiv.appendChild(item);
        });
        outputDiv.innerHTML += "</ul>";
    };

    // 평가 점수의 유효성을 검사하는 함수
    const isValidRating = (rating) => {
        const regex = /^([0-5](?:\.[0-9]?)?)$/; // 0에서 5 사이의 소수점 한자리까지 허용
        return regex.test(rating);
    };

    // 로그인 버튼 클릭 이벤트 등록
    document.getElementById("login-btn").addEventListener("click", () => {
        userId = userIdInput.value.trim();
        if (userId) {
            connectToServer();
            sendRequest({ request_type: "INITIALIZE_USER", user_id: userId }); // 새로운 사용자 초기화
            showSection(menuSection);
        } else {
            alert("사용자 ID를 입력하세요.");
        }
    });

    // 추천 장르 목록 버튼 클릭 이벤트 등록
    document.getElementById("genre-btn").addEventListener("click", () => {
        sendRequest({ request_type: "GET_GENRES" });
    });

    // 사용자 맞춤형 도서 장르 추천 버튼 클릭 이벤트 등록
    document.getElementById("recommend-genre-btn").addEventListener("click", () => {
        console.log("사용자 맞춤형 도서 장르 추천 요청 전송");
        sendRequest({ request_type: "RECOMMEND_CUSTOM_GENRE", user_id: userId });
    });

    // 장르 선택 화면에서 뒤로가기 버튼 클릭 이벤트 등록
    document.getElementById("back-btn-from-genre").addEventListener("click", () => {
        showSection(menuSection);
    });

    // 추천 도서 화면에서 뒤로가기 버튼 클릭 이벤트 등록
    document.getElementById("back-btn").addEventListener("click", () => {
        showSection(menuSection);
    });

    // 프로그램 종료 버튼 클릭 이벤트 등록
    document.getElementById("exit-btn").addEventListener("click", () => {
        alert("프로그램을 종료합니다.");
        socket.disconnect();
        location.reload();
    });
});
