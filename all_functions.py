import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
import os
import pass_to_server
from IPython.display import Image, display
from datetime import datetime
from functools import lru_cache
import webbrowser
import logging


# ---------------------------------------------------------------------------- Configuring logging of connection and disconnection to the database --- #

logging.basicConfig(
    filename='database_connections.log',                               # File name for logging
    level=logging.INFO,                                                # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s'                 # Message format
)

# ------------------------------------------------------------------- Connection --------------------------------------------------------------------- #
# **************************************************************************************************************************************************** #

# ------------------------------------------------------------------------------------------------ Connecting to the local *** sakila *** database --- #

def connect_to_sakila():
    try:
        connection = mysql.connector.connect(host=pass_to_server.host_ls, user=pass_to_server.user_ls, password=pass_to_server.password_ls, database=pass_to_server.database_ls)
        if connection.is_connected():
            logging.info("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error while connecting to database *sakila*: {str(e)}")
        return None     

# ------------------------------------------------------------------------------------------------------- Подключение к локальной базе данных logs --- #

def connect_to_logs():                               
    try:
        log_connection = mysql.connector.connect(host=pass_to_server.host_l, user=pass_to_server.user_l, password=pass_to_server.password_l, database=pass_to_server.database_l)
        if log_connection.is_connected():
            logging.info("Successfully connected to the database")    
            return log_connection
    except Error as e:
        print(f"Error while connecting to database *logs*: {str(e)}")
        return None      

# ----------------------------------------------------------------------------------------------------------- Execution of SQL queries and caching --- #

@lru_cache(maxsize=32)                                                # Set the maximum cache size
def execute_query(query):
    connection = connect_to_sakila()                                  
    cursor = connection.cursor()                                      # the cursor is needed to execute SQL queries
    try:
        cursor.execute(query)                                         # SQL queries are executed here
        rows = cursor.fetchall()                                      # get the list of tuples
        columns = [desc[0] for desc in cursor.description]            # list of column names 
        dicts = [dict(zip(columns, row)) for row in rows]             # Create a dictionary with merged column names with corresponding tuple values
        return dicts      
    except Exception as e:
        print(f"Request execution error: {str(e)}")
        return None
    finally:
        cursor.close()
        connection.close()



# ----------------------------------------------------------- Stastics of user requests -------------------------------------------------------------- #
# **************************************************************************************************************************************************** #

# --------------------------------------------------------------------------------------- Decorator for logging user requests and invoking details --- #

def handle_search_log_details(func):
    def wrapper(*args, **kwargs):
        log_prefix = kwargs.pop('log_prefix', '')
                                                                        
        result_for_decor = func()                                       # the main function should return (results, input_value)

        if not result_for_decor or not isinstance(result_for_decor, tuple) or len(result_for_decor) != 2:
            print("Error: the function should return (results, input_value)")
            return

        results, input_value = result_for_decor

        if results:
            if log_prefix:
                log_query(log_prefix, input_value)
            print_results_1_4(results)
        else:
            print("Nothing found / invalid input.")
    return wrapper

# ------------------------------------------------------------------------- Inserting a user query into the “queries” table of the “logs” database --- #

def log_query(query_type, value):
    """
    query_type: str - query type, e.g. 'keyphrase', 'genre', 'year', 'actor'
    value: str or list - query value (e.g. 'drama' or ['Egg', 'gold'])
    """
    log_connection = connect_to_logs()
    log_cursor = log_connection.cursor()

    try:
        query_time = datetime.now()
        if isinstance(value, list):
            query_value = " ".join(map(str, value))
        else:
            query_value = str(value)

        sql = """
        INSERT INTO queries (query_type, query_value, query_time)
        VALUES (%s, %s, %s)
        """
        # print(f"[log_query] type: {query_type}, value: {value}")
        # print(f"[log_query] value: {query_value}")
        log_cursor.execute(sql, (query_type, query_value, query_time))
        log_connection.commit()

    except Exception as e:
        print(f"Query logging error: {str(e)}")
    finally:
        log_cursor.close()
        log_connection.close()



# ------------------------------------------------------------------ Service requests ---------------------------------------------------------------- #
# **************************************************************************************************************************************************** #

# ------------------------------------------------------------------------------------------------------------------------ Getting popular queries --- #

def get_popular_queries():
    # log_query("get_popular_queries", "yes")                     # you can enable logging of this request 

    log_connection = connect_to_logs()
    log_cursor = log_connection.cursor()

    query = """
    SELECT 
        query_type AS TypeQuery,
        query_value AS ValueQuery,
        COUNT(*) AS CountQueries
    FROM queries
    GROUP BY query_type, query_value
    ORDER BY CountQueries DESC
    LIMIT 3
    """
    
    try:
        log_cursor.execute(query)
        rows = log_cursor.fetchall()                            # get the list of tuples
        columns = [desc[0] for desc in log_cursor.description]  # list of column names 
        dicts = [dict(zip(columns, row)) for row in rows]       # Create a dictionary with merged column names with corresponding tuple values
        return dicts 
    except Exception as e:
        print(f"Request execution error: {str(e)}")
        return None
    finally:
        log_cursor.close()
        log_connection.close()

# --------------------------------------------------------------------------------------------------------- Instructions on how to use the program --- #

def show_help():
    help_file = "help.txt"
    try:
        with open(help_file, "r", encoding="utf-8") as f:
            text = f.readlines()
            for str_ in text:
                print(str_.strip())
    except FileNotFoundError:
        print(f"Instruction file not found: {help_file}")
    except Exception as e:
        print(f"Error reading the instruction file: {e}")



# ------------------------------------------------------- Queries to the *** sakila *** database ----------------------------------------------------- #
# **************************************************************************************************************************************************** #
        
query_general_part_SELECT_FROM_JOIN = """
    SELECT 
        f.film_id Film_id,
        f.title Title, 
        f.description Description, 
        f.release_year Release_year,
        f.rental_rate Rental_rate,
        f.length Length,
        f.rating Rating,
        c.name Category,
        GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') AS Actors
    FROM film f
    LEFT JOIN film_actor fa ON f.film_id = fa.film_id
    LEFT JOIN actor a ON fa.actor_id = a.actor_id
    LEFT JOIN film_category fc ON f.film_id = fc.film_id
    LEFT JOIN category c ON fc.category_id = c.category_id        
"""
query_general_part_GROUP_ORDER = """
    GROUP BY
        f.film_id,
        f.title,
        f.description,
        f.release_year,
        f.rental_rate,
        f.length,
        f.rating,
        c.name
    ORDER BY f.film_id
"""

# --------------------------------------------------------------------------------------------------------------------- Key phrase search function --- #

@handle_search_log_details
def search_by_keyphrase():
    punctuation_chars = ".,!?;:-_()[]{}\"'`…/\\|<>@#$%^&*~+="

    while True:
        text = input("Enter a key phrase or word: ").strip()
        if not text:
            print("Blank Input. Try again.\n")
            continue

        cleaned_text = ""
        for char in text:
            if char in punctuation_chars:
                cleaned_text += " "
            else:
                cleaned_text += char
        keyphrase = cleaned_text.lower().split()

        if not keyphrase:
            print("Nothing was found for the words entered. Try again.\n")
            continue

        query_kp = " AND ".join([f"(f.title LIKE '%{kp}%' OR f.description LIKE '%{kp}%')" for kp in keyphrase])
        query = f"""
            {query_general_part_SELECT_FROM_JOIN}
            WHERE {query_kp}
            {query_general_part_GROUP_ORDER}
        """     
        return execute_query(query), keyphrase

# ------------------------------------------------------------------------------------------------------------------------- Other search functions --- #

@handle_search_log_details
def search_by_genre():
    all_genres = [
        "Action", "Animation", "Children", "Classics", "Comedy", "Documentary", "Drama", "Family", "Foreign", "Games", "Horror", "Music", "New", "Sci-Fi", "Sports", "Travel"
    ]
    genre = input(f'''Enter a genre from the list:\n{', '.join(all_genres)}   \n''').strip()
    if not genre:
        print("Неверный ввод.\n")
        return None, genre
    query = f"""
        {query_general_part_SELECT_FROM_JOIN}
        WHERE c.name = '{genre}'
        {query_general_part_GROUP_ORDER}
    """
    return execute_query(query), genre


@handle_search_log_details
def search_by_year():
    try:
        all_years = ['2006']
        year = int(input(f"Enter the year from the list: {', '.join(all_years)} ").strip())
    except ValueError:
        print("Invalid entry. Enter a number.\n")
        return None, None
    query = f"""
        {query_general_part_SELECT_FROM_JOIN}
        WHERE f.release_year = '{year}'
        {query_general_part_GROUP_ORDER}
    """
    return execute_query(query), year


@handle_search_log_details
def search_by_actor():
    part_actors_first = ['AUDREY', 'JOHN', 'JAYNE']
    part_actors_last = ['BAILEY', 'SUVARI', 'SILVERSTONE']
    fname = input(f"Actor's name: {', '.join(part_actors_first)} и т.д.   \n").strip()
    lname = input(f"Actor's last name: {', '.join(part_actors_last)} и т.д.   \n").strip()
    if not fname or not lname:
        print("First and last name required.\n")
        return None, f"{fname} {lname}"
    query = f"""
        {query_general_part_SELECT_FROM_JOIN}
        WHERE a.first_name = '{fname}' AND a.last_name = '{lname}'
        {query_general_part_GROUP_ORDER}
    """
    return execute_query(query), f"{fname} {lname}"


def top_rented_films():
    query = """
    	SELECT 
    		ROW_NUMBER() OVER (ORDER BY COUNT(f.film_id) DESC) AS N,
    		f.title Title,
    		COUNT(f.film_id) AS Rental_count,
            RANK() OVER(ORDER BY COUNT(f.film_id) DESC) Rental_rank
    	FROM rental r
    	JOIN inventory i ON r.inventory_id = i.inventory_id
    	JOIN film f ON i.film_id = f.film_id
    	GROUP BY f.film_id
    	ORDER BY Rental_count DESC
    	LIMIT 10
    """
    return execute_query(query)


def top_busy_actors():
    query = """
    	SELECT 
    		ROW_NUMBER() OVER (ORDER BY COUNT(a.actor_id) DESC) AS N,
            a.first_name First_name, 
            a.last_name Last_name, 
            COUNT(*) AS Film_count,
            RANK() OVER(ORDER BY COUNT(a.actor_id) DESC) Actor_rank
    	FROM film_actor fa
    	JOIN actor a ON fa.actor_id = a.actor_id
    	GROUP BY a.actor_id
    	ORDER BY film_count DESC
    	LIMIT 10
    """
    return execute_query(query)


def price_categories():
    query = """
		SELECT
			GROUP_CONCAT(f.title SEPARATOR ', ') AS Titles,
            f.rental_rate Rental_rate,
            c.name Category
        FROM film f
		LEFT JOIN film_category fc ON f.film_id = fc.film_id
		LEFT JOIN category c ON fc.category_id = c.category_id
        GROUP BY f.rental_rate, c.name
        ORDER BY Rental_rate DESC
    """
    return execute_query(query)

def movie_categories_by_duration():
    query = """
        SELECT 
			ROW_NUMBER() OVER (ORDER BY Length DESC) AS N,
            length Length,
            GROUP_CONCAT(title SEPARATOR ', ') AS Titles
        FROM film
        GROUP BY Length
        ORDER BY length DESC
    """
    return execute_query(query)


def latest_rentals():
    query = """
		SELECT 
			ROW_NUMBER() OVER (ORDER BY DATE(r.rental_date) DESC) AS N,
			f.title, 
			DATE(r.rental_date) AS rental_date
		FROM rental r
		JOIN inventory i ON r.inventory_id = i.inventory_id
		JOIN film f ON i.film_id = f.film_id
		ORDER BY r.rental_date DESC
		LIMIT 10
    """
    return execute_query(query)



# --------------------------------------------------------- User menu and print results -------------------------------------------------------------- #
# **************************************************************************************************************************************************** #

# --------------------------------------------------------------------------------------------------------------------------- Image "Movie Search" --- #

def show_image_search():
    # image_path = r"C:\Users\91500\Documents\ICH\Lessons\3 Python\3 Project\Images_for_project\MovieSearch.jpg"
    image_path = r"MovieSearch.jpg"
    try:
        display(Image(filename=image_path))
    except Exception as e:
        print(f"Failed to load the image: {e}")

# --------------------------------------------------------------------------------------------------------------------------------- Output of MENU --- #

def print_menu():
    menu_items = [
        ("1.",  chr(0x1F50D), "Search by keyword or phrase"),                                
        ("2.",  chr(0x1F3AC), "Search by genre"),                                                   
        ("3.",  chr(0x1F4C5), "Search by year"),                                                    
        ("4.",  chr(0x1F9D1), "Search by actor"),
        ("5.",  chr(0x1F4B5), "Movie price categories by genre"), 
        ("6.",  chr(0x1F3C6), "Top 10 popular movies (most rented in our stores)"),
        ("7.",  chr(0x1F3AD), "Top 10 actors (the most frequently seen actors in the movies in our database)"),                                              
        ("8.",  chr(0x1F552), "Categories of movies by duration"),                                    
        ("9.",  chr(0x1F4D6), "The last 10 rented movies")                                 
    ]
    
    service_items = [
        ("10.", chr(0x1F4CA), "Top 3 popular user queries"),   
        ("11.", chr(0x1F4AC), "Instructions on how to use the program"),
        ("12.", chr(0x1F4AC), "Structure of *sakila* base (tables, columns)"),
        ("0.",  chr(0x274C),  "Exit")                                     
    ]
    
    print(f'\nSelect a search option:\n')
    for num, emoji, desc in menu_items:
        print(f"{num:<4} {'<<<':^5} {emoji:^3} {'>>>':^5}{" ":^1} {desc}")

    print(f"\nService requests:\n")
    for num, emoji, desc in service_items:
        print(f"{num:<4} {'<<<':^5} {emoji:^3} {'>>>':^5} {desc}")
    print(f'\n ')

# ------------------------------------------------------------------------------------------------------------- Output of results for variants 1-4 --- #

def print_results_1_4(results):
    if not results:
        print("First, enter the search parameters!")
        return

    print("\nList of movies at your request:\n")
    for i, film in enumerate(results, start=1):
        num_str = str(i).rjust(6)
        print(
            f'''{num_str}. Title: {film['Title']}\n'''
            f'''{8 * " "}Release year: {film.get('Release_year', 'no info')} | Rating: {film.get('Rating', 'no info')}\n'''
            f'''{8 * " "}Genre: {film.get('Category', 'no info')}\n'''
            f'''{8 * " "}Actors: {film.get('Actors', 'no info')}\n'''            
            f'''{8 * " "}Description: {film.get('Description', 'no info')}\n'''
            f'''{8 * " "}Rental rate: {film.get('Rental_rate', 'no info')}\n'''             
        )
    try:
        choice = int(input("Enter the movie number from the list above to get information about the availability or unavailability of the movie in the store: ")) - 1
        if choice < 0 or choice >= len(results):
            print("You have entered a number that is not in the list above.")
            return
    except ValueError:
        print("You need to enter a number.")
        return

    selected_film_id = results[choice]['Film_id']
    # check_availability(selected_film_id)
    address_id, store_info = show_availability(selected_film_id)
    show_store_details_and_map(address_id, store_info)

# ----------------------------------------------------------------------- Output of results about availability of movies in stores for options 1-4 --- #

def show_availability(film_id):
    query = f"""
    SELECT 
        ROW_NUMBER() OVER (ORDER BY COUNT(i.store_id) DESC) AS N, 
        f.film_id Film_id,
        f.title Title,
        COUNT(i.inventory_id) Available_copies, 
        i.store_id Store,
        co.country Country,
        c.city City,    
        a.address Address,
        a.district District,
        a.postal_code Postal_caode,
        a.phone Phone_number,
        a.address_id Address_ID
    FROM film f
    JOIN inventory i ON f.film_id = i.film_id
    LEFT JOIN rental r ON i.inventory_id = r.inventory_id
    LEFT JOIN store s ON s.store_id = i.store_id
    LEFT JOIN address a ON s.address_id = a.address_id
    LEFT JOIN city c ON c.city_id = a.city_id
    LEFT JOIN country co ON c.country_id = co.country_id
    WHERE f.film_id = {film_id}
      AND (
            r.return_date IS NOT NULL
            OR r.rental_id IS NULL
          )
    GROUP BY f.film_id, f.title, i.store_id
    """
    result = execute_query(query)
    
    if not result:
        print("No availability information available.")
        return None, None

    print("\nInformation about the availability of a copy of the movie in the store:")
    short_result = [
        {
            'Title': row['Title'],
            'Available_copies': row['Available_copies'],
            'Store': row['Store'],
            'Country': row['Country'],
            'City': row['City']
        }
        for row in result
    ]
    print(tabulate(short_result, headers='keys', tablefmt="grid"))

    try:
        choice = int(input("Select a store and enter its store number: ")) - 1
        if choice < 0 or choice >= len(result):
            print("Wrong number.")
            return None, None
        return result[choice]['Address_ID'], result[choice]
    except ValueError:
        print("You need to enter a number.")
        return None, None

# ---------------------------------------------------------------------------------- Displays detailed information about the store for options 1-4 --- #

def show_store_details_and_map(address_id, store_info):
    if not address_id or not store_info:
        return

    print("\nDetailed information about the store:\n")
    print(
        f"Country: {store_info['Country']}\n"
        f"City: {store_info['City']}\n"
        f"Address: {store_info['Address']}\n"
        f"District: {store_info.get('District', 'n/a')}\n"
        f"Postal Code: {store_info.get('Postal_code', 'n/a')}\n"
        f"Phone: {store_info.get('Phone_number', 'n/a')}\n"
    )

    choice = input("Show the store on a map? (Enter ** y/n **): ").strip().lower()
    if choice == 'y':
        open_location_on_map(address_id)

# --------------------------------------------------------------------------------------------------- Function to open coordinates for options 1-4 --- #

def open_location_on_map(address_id):
    query = f"""
        SELECT 
            ST_X(location) longitude, 
            ST_Y(location) latitude
        FROM address
        WHERE address_id = {address_id}
    """
    result = execute_query(query)
    if result:
        coords = result[0]
        lat = coords["latitude"]
        lon = coords["longitude"]
        print(f'{lat}, {lon}')
        url = f"https://www.google.com/maps?q={lat},{lon}"
        # Example of a link: https://www.google.com/maps/@41.3911056,2.1548483,15
        webbrowser.open(url)
    else:
        print("Coordinates not found.")

# --------------------------------------------------------------------------------------------------------------- Output of results for variants 5 --- #
     
def print_results_5(results):
    if not results:
        print("First, enter the search parameters!")
        return

    print("\nMovie price categories by genre:\n")
    for i, film in enumerate(results, start=1):
        num_str = str(i).rjust(6)
        print(
            f'''{num_str}. Rental rate: {film.get('Rental_rate', 'no info')}\n'''
            f'''{8 * " "}Genre: {film['Category']}\n''' 
            f'''{8 * " "}Titles: {film['Titles']}\n'''    
        )

# ------------------------------------------------------------------------------------------------------------ Output of results for variants 6-10 --- #
        
def print_results_6_10(results):
    if results:
        first_row = results[0]
        headers = []
        for h in first_row:
            headers.append(h)
        rows = []
        for row in results:
            row_values = []
            for h in headers:
                row_values.append(row[h])
            rows.append(row_values)
        print(tabulate(rows, headers, "grid"))
        
    else:
        print("Nothing found.")

# --------------------------------------------------------------------------------------------------------------------------- Image "Movie Search" --- #

def show_image_sakila_structure():
    sakila_tables = r"ER-diag_sakila with columns_final.png"
    sakila_columns = r"ER-diag_sakila_columns.png"
    try:
        display(Image(filename=sakila_tables))
        display(Image(filename=sakila_columns))        
    except Exception as e:
        print(f"Failed to load the image: {e}")

