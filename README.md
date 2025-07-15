# 🎬 Movie Search (SAKILA SQL Project)

Interactive console program in Python for searching and analyzing movies from **SAKILA** database with MySQL connection. Supports searches by keywords, genres, year, actors and displays movie rental statistics.

---

## 🚀 Features

- 🔍 Search movies by keywords  
- 🎬 Search by genre  
- 📅 Search by year of release  
- 🧑 Search by actor name  
- 💰 Display movie price categories by genre  
- 🏆 Top 10 most rented movies  
- 🎭 Top 10 busiest actors  
- 🕒 Movie categories by length  
- 📚 Most recently rented movies  
- 📊 Top 3 popular user requests  
- 🗺️ Opening a store on Google Maps by coordinates from the database  
- 💬 Instruction and visualization of the database structure   

---

## 🛠️ Technologies used

- Python 3 
- MySQL  
- SAKILA database  
- Libraries:
  - `mysql-connector-python`
  - `tabulate`
  - `IPython.display` (for Jupyter)
  - `webbrowser`
  - `logging`
  - `functools`

---

## 📁 Project structure

```
.
├── search_movies.py               # Program entry point
├── all_functions.py               # All functions and SQL queries
├── pass_to_server.py              # Database connection configuration
├── help.txt                       # User manual
├── MovieSearch.jpg                # Program cover
├── ER-diag_sakila_columns.png     # ER-diagram of database structure
└── ER-diag_sakila with columns_final.png
```

---

## ▶️ How to run

1. Install the dependencies:

```bash
pip install mysql-connector-python tabulate
```

2. Fill the `pass_to_server.py` file with the connection parameters:

```python
host_ls = 'localhost'
user_ls = 'root'
password_ls = 'yourpassword'
database_ls = 'sakila'

host_l = 'localhost'
user_l = 'root'
password_l = 'yourpassword'
database_l = 'logs'
```

3. Run from a terminal or PyCharm:

```bash
python search_movies.py
```

---

## 📌 Note

- The project uses `GROUP_CONCAT`, `ROW_NUMBER`, `RANK`, `JOIN` and other SQL features.
- All search queries are logged to the `logs` database.
- You can open store coordinates on Google Maps if you have.

---

## 🧑‍💻 Author

Kirill Mikhalishin 
Project on Python + SQL 
2024-2025
