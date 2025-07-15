
from all_functions import *


# -------------------------------------------------------------------- Basic program ----------------------------------------------------------------- #
# **************************************************************************************************************************************************** #

def search_movies():
    while True:
        print(f"\n")
        show_image_search()                                                         # Image display
        print_menu()                                                                # Displaying the search options selection menu
        choice = input("Select an action: ")
        
        if choice == "1":
            print("\nSearch by keyword or phrase:")
            search_by_keyphrase(log_prefix="keyphrase")

        elif choice == "2":
            print("\nSearch by genre:")
            search_by_genre(log_prefix="genre")
            
        elif choice == "3":
            print("\nSearch by year:")
            search_by_year(log_prefix="year")
            
        elif choice == "4":
            print("\nSearch by actor:")
            search_by_actor(log_prefix="actor")

        elif choice == "5":
            print("\nMovie price categories by genre:")
            results = price_categories()
            print_results_5(results)
            
        elif choice == "6":
            print("\nTop 10 popular movies (most rented in our stores):")
            results = top_rented_films()
            print_results_6_10(results)

        elif choice == "7":
            print("\nTop 10 actors (the most frequently seen actors in the movies in our database):")
            results = top_busy_actors()
            print_results_6_10(results)

        elif choice == "8":
            print("\nCategories of movies by duration:")
            results = movie_categories_by_duration()
            print_results_6_10(results)

        elif choice == "9":
            print("\nThe last 10 rented movies:")
            results = latest_rentals()
            print_results_6_10(results)

        elif choice == "10":
            print("\nTop 3 popular user queries:")
            results = get_popular_queries()
            print_results_6_10(results)
            
        elif choice == "11":
            print("\nInstructions on how to use the program:\n")
            show_help()
            
        elif choice == "12":
            print("\nStructure of *sakila* base (tables, columns):\n")
            show_image_sakila_structure()

        elif choice == "0":
            print("\nWe are glad to see you at our service.\nI'll see you again!")
            break

        else:
            print("\nYou have not entered anything, or you have entered a wrong number from the list of commands provided. Try again.")

if __name__ == "__main__":
    search_movies()
