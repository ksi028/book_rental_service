import streamlit as st
import requests
import uuid


BOOK_API_URL = "http://127.0.0.1:8001/books/"
USER_API_URL = "http://127.0.0.1:8002/users/"
RENT_BOOK_API_URL = "http://127.0.0.1:8002/users/rent/"
RETURN_BOOK_API_URL = "http://127.0.0.1:8002/users/return/"
UPDATE_BOOK_API_URL = "http://127.0.0.1:8001/books/"
DELETE_BOOK_API_URL = "http://127.0.0.1:8001/books/"
DELETE_USER_API_URL = "http://127.0.0.1:8002/users/"
UPDATE_USER_API_URL = "http://127.0.0.1:8002/users/"
AUTH_API_URL = "http://127.0.0.1:8002/login/"


st.set_page_config(page_title="Book Rental Service", page_icon="📚", layout="wide")


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Login to Book Rental Service")

    email = st.text_input("Enter Email", value="admin@example.com")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if email == "admin@example.com" and password == "pass123":
            st.session_state.authenticated = True
            st.success("✅ Login Successful!")
            st.rerun()
        else:
            st.error("⚠ Invalid Credentials. Try Again.")
    st.stop()


st.sidebar.title("📚 Book Rental Dashboard")
category = st.sidebar.radio("Select a Category", ["Manage Books", "Manage Users", "Rental Operations", "Logout"])

if category == "Logout":
    st.session_state.clear()
    st.rerun()

if category == "Manage Books":
    action = st.sidebar.radio("Choose an Action", ["View Books", "Add Book", "Update Book", "Delete Book"])

    if action == "View Books":
        st.title("📖 List of Available Books")
        response = requests.get(BOOK_API_URL)
        if response.status_code == 200:
            books = response.json()
            st.table(books)
        else:
            st.error("⚠ Failed to fetch books.")

    elif action == "Add Book":
        st.title("➕ Add a New Book")
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        genre = st.text_input("Genre")
        available_copies = st.number_input("Available Copies", min_value=1, step=1)

        if st.button("Add Book"):
            book_data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "author": author,
                "genre": genre,
                "available_copies": available_copies
            }
            response = requests.post(BOOK_API_URL, json=book_data)

            if response.status_code == 200:
                st.success(f"📚 '{title}' added successfully!")
            else:
                st.error("⚠ Failed to add book.")

    elif action == "Update Book":
        st.title("✏ Update a Book")
        response = requests.get(BOOK_API_URL)
        if response.status_code == 200:
            books = response.json()
            book_ids = {book["title"]: book["id"] for book in books}
            selected_book = st.selectbox("Select a Book to Update", list(book_ids.keys()))

            book_id = book_ids[selected_book]
            book_data = next(book for book in books if book["id"] == book_id)

            title = st.text_input("Title", value=book_data["title"])
            author = st.text_input("Author", value=book_data["author"])
            genre = st.text_input("Genre", value=book_data["genre"])
            available_copies = st.number_input("Available Copies", min_value=1, step=1, value=book_data["available_copies"])

            if st.button("Update Book"):
                updated_data = {
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "available_copies": available_copies
                }
                update_response = requests.put(f"{UPDATE_BOOK_API_URL}{book_id}", json=updated_data)

                if update_response.status_code == 200:
                    st.success(f"✅ '{title}' updated successfully!")
                else:
                    st.error("⚠ Failed to update book.")

    elif action == "Delete Book":
        st.title("🗑 Delete a Book")
        response = requests.get(BOOK_API_URL)
        if response.status_code == 200:
            books = response.json()
            book_ids = {book["title"]: book["id"] for book in books}
            selected_book = st.selectbox("Select a Book to Delete", list(book_ids.keys()))

            if st.button("Delete Book"):
                book_id = book_ids[selected_book]
                delete_response = requests.delete(f"{DELETE_BOOK_API_URL}{book_id}")

                if delete_response.status_code == 200:
                    st.success(f"✅ '{selected_book}' deleted successfully!")
                else:
                    st.error("⚠ Failed to delete book.")

if category == "Manage Users":
    action = st.sidebar.radio("Choose an Action", ["View Users", "Add User", "Update User", "Delete User"])

    if action == "View Users":
        st.title("👥 List of Users")
        response = requests.get(USER_API_URL)
        if response.status_code == 200:
            users = response.json()
            if users:
                st.table(users)
            else:
                st.info("📭 No users found.")
        else:
            st.error(f"⚠ Failed to fetch users. Error: {response.text}")

    elif action == "Add User":
        st.title("➕ Add a New User")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Add User"):
            user_data = {
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "password": password,
                "rented_books": []
            }
            response = requests.post(USER_API_URL, json=user_data)
            if response.status_code == 200:
                st.success(f"✅ '{name}' added successfully!")
                st.rerun()
            else:
                st.error(f"⚠ Failed to add user. Error: {response.text}")

    elif action == "Update User":
        st.title("✏ Update User Details")
        response = requests.get(USER_API_URL)
        if response.status_code == 200:
            users = response.json()
            if users:
                user_ids = {user["name"]: user["id"] for user in users}
                selected_user = st.selectbox("Select a User to Update", list(user_ids.keys()))

                user_id = user_ids[selected_user]
                user_data = next(user for user in users if user["id"] == user_id)

                new_name = st.text_input("New Name", value=user_data["name"])
                new_email = st.text_input("New Email", value=user_data["email"])
                new_password = st.text_input("New Password", type="password")

                if st.button("Update User"):
                    update_data = {
                        "name": new_name,
                        "email": new_email,
                        "password": new_password if new_password else user_data["password"],
                        "rented_books": user_data["rented_books"]
                    }
                    update_response = requests.put(f"{UPDATE_USER_API_URL}{user_id}", json=update_data)
                    if update_response.status_code == 200:
                        st.success(f"✅ '{selected_user}' updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"⚠ Failed to update user. Error: {update_response.text}")
            else:
                st.warning("⚠ No users found.")

    elif action == "Delete User":
        st.title("🗑 Delete a User")
        response = requests.get(USER_API_URL)
        if response.status_code == 200:
            users = response.json()
            if users:
                user_ids = {user["name"]: user["id"] for user in users}
                selected_user = st.selectbox("Select a User to Delete", list(user_ids.keys()))

                if st.button("Delete User"):
                    user_id = user_ids[selected_user]
                    delete_response = requests.delete(f"{DELETE_USER_API_URL}{user_id}")
                    if delete_response.status_code == 200:
                        st.success(f"✅ '{selected_user}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error(f"⚠ Failed to delete user. Error: {delete_response.text}")
            else:
                st.warning("⚠ No users available for deletion.")



if category == "Rental Operations":
    st.title("📖 Rental Operations")
    rental_action = st.radio("Select an Action", ["Rent a Book", "Return a Book", "View Rental History"])

    if rental_action == "Rent a Book":
        st.subheader("📚 Rent a Book")
        user_response = requests.get(USER_API_URL)
        book_response = requests.get(BOOK_API_URL)

        if user_response.status_code == 200 and book_response.status_code == 200:
            users = user_response.json()
            books = book_response.json()
            available_books = [book for book in books if book["available_copies"] > 0]

            if not users or not available_books:
                st.warning("⚠ No users or available books.")
            else:
                user_names = {user["name"]: user["id"] for user in users}
                book_titles = {book["title"]: book["id"] for book in available_books}

                selected_user = st.selectbox("Select User", list(user_names.keys()))
                selected_book = st.selectbox("Select Book", list(book_titles.keys()))

                if st.button("Rent Book"):
                    rent_response = requests.post(
                        f"{RENT_BOOK_API_URL}{user_names[selected_user]}/{book_titles[selected_book]}"
                    )

                    if rent_response.status_code == 200:
                        st.success(f"✅ '{selected_book}' rented successfully by {selected_user}!")
                    else:
                        st.error(f"⚠ Failed to rent book. Error: {rent_response.text}")

    elif rental_action == "Return a Book":
        st.subheader("📚 Return a Book")
        user_response = requests.get(USER_API_URL)
        book_response = requests.get(BOOK_API_URL)

        if user_response.status_code == 200 and book_response.status_code == 200:
            users = user_response.json()
            books = book_response.json()
            book_dict = {book["id"]: book["title"] for book in books}

            users_with_books = [user for user in users if user["rented_books"]]

            if not users_with_books:
                st.warning("⚠ No users have rented books.")
            else:
                user_names = {user["name"]: user["id"] for user in users_with_books}
                selected_user = st.selectbox("Select User", list(user_names.keys()))

                user_id = user_names[selected_user]
                user_data = next(user for user in users if user["id"] == user_id)
                rented_books = user_data["rented_books"]

                if not rented_books:
                    st.warning(f"⚠ {selected_user} has no rented books.")
                else:
                    rented_book_options = {book_dict.get(book_id, f"Unknown Book ({book_id})"): book_id
                                           for book_id in rented_books}

                    selected_book_title = st.selectbox("Select Book to Return", list(rented_book_options.keys()))
                    selected_book_id = rented_book_options[selected_book_title]

                    if st.button("Return Book"):
                        return_response = requests.post(
                            f"{RETURN_BOOK_API_URL}{user_id}/{selected_book_id}"
                        )

                        if return_response.status_code == 200:
                            st.success(f"✅ '{selected_book_title}' returned successfully by {selected_user}!")
                            st.rerun()
                        else:
                            st.error(f"⚠ Failed to return book. Error: {return_response.text}")

    elif rental_action == "View Rental History":
        st.subheader("📜 Rental History")
        user_response = requests.get(USER_API_URL)
        book_response = requests.get(BOOK_API_URL)

        if user_response.status_code == 200 and book_response.status_code == 200:
            users = user_response.json()
            books = book_response.json()
            book_dict = {book["id"]: book["title"] for book in books}

            history = [{"User": user["name"], "Book": book_dict.get(book_id, "Unknown")}
                       for user in users if user["rented_books"] for book_id in user["rented_books"]]

            if history:
                st.table(history)
            else:
                st.info("📖 No rental history available.")