from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import List
import sqlite3
import httpx

app = FastAPI()


conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    password TEXT,
    rented_books TEXT
)
""")
conn.commit()



class User(BaseModel):
    name: str
    email: str
    password: str
    rented_books: List[str] = []



@app.post("/users/")
def add_user(user: User):
    user_id = str(uuid4())
    cursor.execute(
        "INSERT INTO users (id, name, email, password, rented_books) VALUES (?, ?, ?, ?, ?)",
        (user_id, user.name, user.email, user.password, ",".join(user.rented_books)),
    )
    conn.commit()
    return {"id": user_id, **user.dict()}



@app.get("/users/")
def list_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return [
        {"id": user[0], "name": user[1], "email": user[2], "rented_books": user[4].split(",") if user[4] else []}
        for user in users
    ]


@app.put("/users/{user_id}")
def update_user(user_id: str, user: User):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_record = cursor.fetchone()

    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    updated_name = user.name if user.name else user_record[1]
    updated_email = user.email if user.email else user_record[2]
    updated_password = user.password if user.password else user_record[3]

    cursor.execute(
        "UPDATE users SET name=?, email=?, password=? WHERE id=?",
        (updated_name, updated_email, updated_password, user_id),
    )
    conn.commit()
    return {"message": "User updated successfully"}



@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_record = cursor.fetchone()

    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()

    return {"message": f"User {user_record[1]} deleted successfully"}






@app.post("/users/rent/{user_id}/{book_id}")
async def rent_book(user_id: str, book_id: str):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rented_books = user[4].split(",") if user[4] else []

    if book_id in rented_books:
        raise HTTPException(status_code=400, detail="User has already rented this book")

    async with httpx.AsyncClient() as client:
        book_response = await client.put(f"http://127.0.0.1:8001/books/{book_id}/decrement")

    if book_response.status_code != 200:
        raise HTTPException(status_code=book_response.status_code, detail="Error updating book copies")

    rented_books.append(book_id)

    cursor.execute("UPDATE users SET rented_books=? WHERE id=?", (",".join(rented_books), user_id))
    conn.commit()

    return {"message": f"Book rented successfully to {user[1]}"}



@app.post("/users/return/{user_id}/{book_id}")
async def return_book(user_id: str, book_id: str):
    cursor.execute("SELECT rented_books FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rented_books = user[0].split(",") if user[0] else []

    if book_id not in rented_books:
        raise HTTPException(status_code=400, detail="Book not rented by user")

    rented_books.remove(book_id)

    cursor.execute("UPDATE users SET rented_books=? WHERE id=?", (",".join(rented_books), user_id))
    conn.commit()

    async with httpx.AsyncClient() as client:
        book_response = await client.put(f"http://127.0.0.1:8001/books/{book_id}/increment")

    if book_response.status_code != 200:
        raise HTTPException(status_code=book_response.status_code, detail="Error updating book copies")

    return {"message": f"Book returned successfully by {user_id}"}



@app.get("/users/rental-history/{user_id}")
def get_rental_history(user_id: str):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rented_books = user[4].split(",") if user[4] else []

    return {"user_id": user[0], "user_name": user[1], "rented_books": rented_books}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
