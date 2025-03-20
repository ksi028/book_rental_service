from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import sqlite3

app = FastAPI()


conn = sqlite3.connect("books.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT,
    author TEXT,
    genre TEXT,
    available_copies INTEGER
)
""")
conn.commit()


class Book(BaseModel):
    title: str
    author: str
    genre: str
    available_copies: int


@app.post("/books/")
def add_book(book: Book):
    book_id = str(uuid4())
    cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?)", (book_id, book.title, book.author, book.genre, book.available_copies))
    conn.commit()
    return {"id": book_id, **book.dict()}


@app.get("/books/")
def list_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    return [{"id": book[0], "title": book[1], "author": book[2], "genre": book[3], "available_copies": book[4]} for book in books]


@app.get("/books/{book_id}")
def get_book(book_id: str):
    cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"id": book[0], "title": book[1], "author": book[2], "genre": book[3], "available_copies": book[4]}



@app.put("/books/{book_id}")
def update_book(book_id: str, book: Book):
    cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
    existing_book = cursor.fetchone()

    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")

    cursor.execute("UPDATE books SET title=?, author=?, genre=?, available_copies=? WHERE id=?",
                   (book.title, book.author, book.genre, book.available_copies, book_id))
    conn.commit()

    return {"message": "Book updated successfully"}



@app.put("/books/{book_id}/decrement")
def decrement_available_copies(book_id: str):
    cursor.execute("SELECT available_copies FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    available_copies = book[0]

    if available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies available")

    updated_copies = available_copies - 1
    cursor.execute("UPDATE books SET available_copies=? WHERE id=?", (updated_copies, book_id))
    conn.commit()

    return {"message": f"Book ID {book_id} now has {updated_copies} copies left."}



@app.put("/books/{book_id}/increment")
def increment_available_copies(book_id: str):
    cursor.execute("SELECT available_copies FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    updated_copies = book[0] + 1
    cursor.execute("UPDATE books SET available_copies=? WHERE id=?", (updated_copies, book_id))
    conn.commit()

    return {"message": f"Book ID {book_id} now has {updated_copies} copies available."}


@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    return {"message": "Book deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

