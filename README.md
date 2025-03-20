
# 📚 Book Rental Service

A FastAPI-based microservice system for managing book rentals, users, and books.

## 🚀 Features

### 📖 Book Service
- CRUD operations for books (Add, Update, Delete, List).
- Stores book details: title, author, genre, and available copies.

### 👤 User Service
- CRUD operations for users.
- Manages rental history and book rentals.
- Handles book rental and return logic.

### 🔄 Inter-Service Communication
- Book and User services communicate via REST APIs.
- Ensures separation of concerns and maintainability.

### 🗄️ Database
- Uses SQLite with separate databases for each service.

### ✅ Validations
- Users **cannot** rent the same book twice.
- Users **cannot** return books they haven't rented.
- Users **cannot** rent books if no copies are available.
- Books **cannot** have negative availability.

---

## 📂 Project Structure
book_rental_service/
├── book_rental_microservice/  
│   ├── book_service/         
│   │   ├── __pycache__/
│   │   ├── books.db           
│   │   ├── main.py           
│   │   ├── models.py          
│   │   ├── database.py       
│   │   └── users.db          
│   │
│   ├── user_service/         
│   │   ├── app.py            
│   │   ├── books.db          
│   │   ├── users.db          
│   │   ├── main.py           
│   │   ├── models.py         
│   │   ├── database.py   
