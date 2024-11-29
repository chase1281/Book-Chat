import sqlite3

# 데이터베이스 연결 및 테이블 생성
def initialize_database():
    # 데이터베이스 파일 생성 및 연결
    conn = sqlite3.connect('book_chat.db')
    cursor = conn.cursor()

    # 기존 중복 데이터 제거를 위한 쿼리
    cursor.execute(''' 
    DELETE FROM books
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM books
        GROUP BY title, author
    )
    ''')

    # books 테이블 생성 (title과 author에 대한 고유 제약 조건 추가)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT NOT NULL,
        UNIQUE(title, author) -- title과 author의 고유 제약 조건 추가
    )
    ''')

    # user_requests 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_requests (
        user_id TEXT NOT NULL,
        genre TEXT NOT NULL,
        request_count INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, genre)
    )
    ''')

    # book_ratings 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS book_ratings (
        book_id INTEGER,
        user_id TEXT NOT NULL,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        PRIMARY KEY (book_id, user_id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
    ''')

    # 100권의 샘플 데이터
    sample_books = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction'),
        ('1984', 'George Orwell', 'Dystopia'),
        ('Moby-Dick', 'Herman Melville', 'Adventure'),
        ('Pride and Prejudice', 'Jane Austen', 'Romance'),
        ('To Kill a Mockingbird', 'Harper Lee', 'Fiction'),
        ('Brave New World', 'Aldous Huxley', 'Dystopia'),
        ('The Catcher in the Rye', 'J.D. Salinger', 'Fiction'),
        ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy'),
        ('War and Peace', 'Leo Tolstoy', 'Historical'),
        ('Crime and Punishment', 'Fyodor Dostoevsky', 'Psychological'),
        ('The Odyssey', 'Homer', 'Classic'),
        ('Frankenstein', 'Mary Shelley', 'Horror'),
        ('Dracula', 'Bram Stoker', 'Horror'),
        ('The Divine Comedy', 'Dante Alighieri', 'Classic'),
        ('Don Quixote', 'Miguel de Cervantes', 'Classic'),
        ('Jane Eyre', 'Charlotte Brontë', 'Romance'),
        ('Wuthering Heights', 'Emily Brontë', 'Romance'),
        ('The Picture of Dorian Gray', 'Oscar Wilde', 'Philosophical'),
        ('Les Misérables', 'Victor Hugo', 'Historical'),
        ('Fahrenheit 451', 'Ray Bradbury', 'Dystopia'),
        ('The Road', 'Cormac McCarthy', 'Dystopia'),
        ('The Shining', 'Stephen King', 'Horror'),
        ('The Name of the Rose', 'Umberto Eco', 'Mystery'),
        ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez', 'Magical Realism'),
        ('The Brothers Karamazov', 'Fyodor Dostoevsky', 'Psychological'),
        ('Anna Karenina', 'Leo Tolstoy', 'Romance'),
        ('The Grapes of Wrath', 'John Steinbeck', 'Historical'),
        ('The Old Man and the Sea', 'Ernest Hemingway', 'Adventure'),
        ('The Count of Monte Cristo', 'Alexandre Dumas', 'Adventure'),
        ('The Stranger', 'Albert Camus', 'Philosophical'),
        ('Gone with the Wind', 'Margaret Mitchell', 'Historical'),
        ('Slaughterhouse-Five', 'Kurt Vonnegut', 'Science Fiction'),
        ('Catch-22', 'Joseph Heller', 'Satire'),
        ('The Bell Jar', 'Sylvia Plath', 'Psychological'),
        ('Beloved', 'Toni Morrison', 'Historical'),
        ('Lord of the Flies', 'William Golding', 'Adventure'),
        ('Ulysses', 'James Joyce', 'Classic'),
        ('The Iliad', 'Homer', 'Classic'),
        ('Middlemarch', 'George Eliot', 'Classic'),
        ('Madame Bovary', 'Gustave Flaubert', 'Classic'),
        ('The Wind-Up Bird Chronicle', 'Haruki Murakami', 'Magical Realism'),
        ('Norwegian Wood', 'Haruki Murakami', 'Romance'),
        ('Memoirs of a Geisha', 'Arthur Golden', 'Historical'),
        ('The Kite Runner', 'Khaled Hosseini', 'Historical'),
        ('Life of Pi', 'Yann Martel', 'Adventure'),
        ('Shogun', 'James Clavell', 'Historical'),
        ('The Secret Garden', 'Frances Hodgson Burnett', 'Children'),
        ('The Little Prince', 'Antoine de Saint-Exupéry', 'Philosophical'),
        ('Charlotte\'s Web', 'E.B. White', 'Children'),
        ('The Call of the Wild', 'Jack London', 'Adventure'),
        ('Heart of Darkness', 'Joseph Conrad', 'Classic'),
        ('The Handmaid\'s Tale', 'Margaret Atwood', 'Dystopia'),
        ('The Fault in Our Stars', 'John Green', 'Romance'),
        ('Percy Jackson and the Olympians', 'Rick Riordan', 'Fantasy'),
        ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', 'Fantasy'),
        ('The Hunger Games', 'Suzanne Collins', 'Dystopia'),
        ('Dune', 'Frank Herbert', 'Science Fiction'),
        ('The Da Vinci Code', 'Dan Brown', 'Thriller'),
        ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 'Mystery'),
        ('The Silence of the Lambs', 'Thomas Harris', 'Thriller'),
        ('A Game of Thrones', 'George R.R. Martin', 'Fantasy'),
        ('The Maze Runner', 'James Dashner', 'Science Fiction'),
        ('Divergent', 'Veronica Roth', 'Dystopia'),
        ('Ender\'s Game', 'Orson Scott Card', 'Science Fiction'),
        ('Foundation', 'Isaac Asimov', 'Science Fiction'),
        ('Neuromancer', 'William Gibson', 'Cyberpunk'),
        ('Do Androids Dream of Electric Sheep?', 'Philip K. Dick', 'Science Fiction'),
        ('The Stand', 'Stephen King', 'Horror'),
        ('The Exorcist', 'William Peter Blatty', 'Horror'),
        ('The Time Traveler\'s Wife', 'Audrey Niffenegger', 'Romance'),
        ('The Shadow of the Wind', 'Carlos Ruiz Zafón', 'Mystery'),
        ('Angels & Demons', 'Dan Brown', 'Thriller'),
        ('The Girl on the Train', 'Paula Hawkins', 'Mystery'),
        ('Big Little Lies', 'Liane Moriarty', 'Thriller'),
        ('Gone Girl', 'Gillian Flynn', 'Thriller'),
        ('The Martian', 'Andy Weir', 'Science Fiction'),
        ('Ready Player One', 'Ernest Cline', 'Science Fiction'),
        ('The Power of Now', 'Eckhart Tolle', 'Self-help'),
        ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology'),
        ('Sapiens', 'Yuval Noah Harari', 'History'),
        ('Atomic Habits', 'James Clear', 'Self-help'),
        ('Educated', 'Tara Westover', 'Biography'),
        ('Becoming', 'Michelle Obama', 'Biography'),
        ('Quiet', 'Susan Cain', 'Psychology'),
        ('12 Rules for Life', 'Jordan Peterson', 'Philosophy'),
        ('Man\'s Search for Meaning', 'Viktor Frankl', 'Philosophy'),
        ('The Four Agreements', 'Don Miguel Ruiz', 'Self-help'),
        ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 'Self-help'),
        ('The Road Less Traveled', 'M. Scott Peck', 'Psychology'),
        ('Outliers', 'Malcolm Gladwell', 'Psychology'),
        ('Grit', 'Angela Duckworth', 'Psychology'),
        ('You Are a Badass', 'Jen Sincero', 'Self-help'),
        ('The Secret', 'Rhonda Byrne', 'Self-help')
    ]

    # 샘플 데이터 삽입
    cursor.executemany('INSERT OR IGNORE INTO books (title, author, genre) VALUES (?, ?, ?)', sample_books)

    # 변경 사항 커밋 및 연결 종료
    conn.commit()
    conn.close()

# 데이터베이스 초기화 호출
initialize_database()
