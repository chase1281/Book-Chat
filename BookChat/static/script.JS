document.addEventListener("DOMContentLoaded", () => {
    const loginSection = document.getElementById("login-section");
    const menuSection = document.getElementById("menu-section");
    const outputSection = document.getElementById("output-section");
    const userIdInput = document.getElementById("user-id");
    const outputDiv = document.getElementById("output");

    const baseURL = "http://127.0.0.1:5555"; // 서버 주소
    let userId = "";

    const showSection = (section) => {
        loginSection.classList.add("hidden");
        menuSection.classList.add("hidden");
        outputSection.classList.add("hidden");
        section.classList.remove("hidden");
    };

    const sendRequest = async (requestData) => {
        try {
            const response = await fetch(baseURL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestData)
            });
            return await response.json();
        } catch (error) {
            return { status: "error", message: "서버 연결 실패" };
        }
    };

    document.getElementById("login-btn").addEventListener("click", () => {
        userId = userIdInput.value.trim();
        if (userId) {
            showSection(menuSection);
        } else {
            alert("사용자 ID를 입력하세요.");
        }
    });

    document.getElementById("genre-btn").addEventListener("click", async () => {
        const genresResponse = await sendRequest({ request_type: "GET_GENRES" });
        if (genresResponse.status === "success") {
            const genres = genresResponse.data.join(", ");
            const genre = prompt(`가능한 장르 목록: ${genres}\n추천받고 싶은 장르를 입력하세요:`);
            if (genre) {
                const booksResponse = await sendRequest({ request_type: "RECOMMEND", genre });
                if (booksResponse.status === "success") {
                    outputDiv.innerHTML = booksResponse.data.map(book => 
                        `<p>ID: ${book.book_id}, 제목: ${book.title}, 저자: ${book.author}, 평가 점수: ${book.avg_rating}</p>`
                    ).join("");
                    showSection(outputSection);
                } else {
                    alert(booksResponse.message);
                }
            }
        } else {
            alert(genresResponse.message);
        }
    });

    document.getElementById("user-btn").addEventListener("click", async () => {
        const userResponse = await sendRequest({ request_type: "RECOMMEND_USER", user_id: userId });
        if (userResponse.status === "success") {
            outputDiv.innerHTML = userResponse.data.map(book =>
                `<p>ID: ${book.book_id}, 제목: ${book.title}, 저자: ${book.author}, 평가 점수: ${book.avg_rating}</p>`
            ).join("");
            showSection(outputSection);
        } else {
            alert(userResponse.message);
        }
    });

    document.getElementById("rate-btn").addEventListener("click", async () => {
        const bookId = prompt("평가할 도서의 ID를 입력하세요:");
        const rating = prompt("도서에 대한 평가 점수 (1~5)를 입력하세요:");
        if (bookId && rating) {
            const rateResponse = await sendRequest({ 
                request_type: "RATE_BOOK", 
                book_id: parseInt(bookId), 
                user_id: userId, 
                rating: parseInt(rating) 
            });
            alert(rateResponse.message);
        }
    });

    document.getElementById("exit-btn").addEventListener("click", () => {
        alert("프로그램을 종료합니다.");
        location.reload();
    });

    document.getElementById("back-btn").addEventListener("click", () => {
        showSection(menuSection);
    });
});
