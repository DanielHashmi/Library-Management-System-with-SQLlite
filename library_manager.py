import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Library Management System",
                   page_icon="📚", layout="wide")

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def run_query(query, params=(), fetch='all', commit=False, return_rowcount=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    result = None
    if commit:
        conn.commit()
        if return_rowcount:
            result = cursor.rowcount
    else:
        if fetch == 'all':
            result = cursor.fetchall()
        elif fetch == 'one':
            result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def initialize_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS books (
       id INT AUTO_INCREMENT PRIMARY KEY,
       Title VARCHAR(255),
       Author VARCHAR(255),
       Publication_Year VARCHAR(4),
       Genre VARCHAR(255),
       Read_Status VARCHAR(10)
    );
    """
    run_query(create_table_query, commit=True)

initialize_table()

def add_a_book():
    st.header('💾 Add a Book')
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input('Title', key="add_title")
        author = st.text_input('Author', key="add_author")
        publication_year = st.text_input('Publication Year', key="add_year")
    with col2:
        genre = st.text_input('Genre', key="add_genre")
        read_status = st.selectbox('Read Status', ['True', 'False'], key="add_status")

    if st.button('Save Book'):
        insert_query = """
        INSERT INTO books (Title, Author, Publication_Year, Genre, Read_Status)
        VALUES (%s, %s, %s, %s, %s)
        """
        run_query(insert_query, (title, author, publication_year, genre, read_status), commit=True)
        st.success(f"Book: '{title}' successfully added")

def remove_a_book():
    st.header('🗑️ Remove a Book')
    title = st.text_input('Title to remove', key="remove_title")
    if st.button('Remove Book'):
        delete_query = "DELETE FROM books WHERE Title = %s"
        rowcount = run_query(delete_query, (title,), commit=True, return_rowcount=True)
        if rowcount > 0:
            st.success(f"Book: '{title}' successfully deleted")
        else:
            st.warning(f"Book: '{title}' not found")

def display_all_books():
    st.header('📕 All Books')
    books = run_query("SELECT * FROM books", fetch='all')
    if books:
        st.dataframe(books, use_container_width=True)
    else:
        st.info("No books available.")

def search_for_a_book():
    st.header('📖 Search for a Book')
    search_by = st.selectbox('Search by', ['Title', 'Author', 'Genre', 'Read_Status'])
    search_term = st.text_input('Enter a search term', key="search_term")
    if search_term:
        query = f"SELECT * FROM books WHERE {search_by} LIKE %s"
        like_term = f"%{search_term}%"
        results = run_query(query, (like_term,), fetch='all')
        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No matching books found.")

def display_statistics():
    st.header('📊 Library Statistics')
    total = run_query("SELECT COUNT(*) as total FROM books", fetch='one')
    total_books = total['total'] if total else 0
    read = run_query("SELECT COUNT(*) as read_count FROM books WHERE Read_Status = 'True'", fetch='one')
    read_books = read['read_count'] if read else 0
    read_percentage = (read_books / total_books * 100) if total_books else 0
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Books", total_books)
    with col2:
        st.metric("Read Books Percentage", f"{read_percentage:.1f}%")

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Select an option:", [
    "Add a Book", "Remove a Book", "Display all Books", "Search for a Book", "Display Statistics"
])

if choice == "Add a Book":
    add_a_book()
elif choice == "Remove a Book":
    remove_a_book()
elif choice == "Display all Books":
    display_all_books()
elif choice == "Search for a Book":
    search_for_a_book()
else:
    display_statistics()
