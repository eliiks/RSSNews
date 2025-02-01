"""
Point d'entrée du programme
"""

from indexation.es_manager import ElasticSearchManager
from collection.rss_parser import RSSParser
from utils.interactions_functions import ask_query, ask_classification

es_manager = ElasticSearchManager("../config/es_config.json")

print(r" ___   ___   ___     ___          _           _   _   _                                ")
print(r"| _ \ / __| / __|   |_ _|  _ _   | |_   ___  | | | | (_)  __ _   ___   _ _    __   ___ ")
print(r"|   / \__ \ \__ \    | |  | ' \  |  _| / -_) | | | | | | / _` | / -_) | ' \  / _| / -_)")
print(r"|_|_\ |___/ |___/   |___| |_||_|  \__| \___| |_| |_| |_| \__, | \___| |_||_| \__| \___|")
print(r"                                                         |___/                         ")


list_menu = ["1", "2", "3", "4", "5"]
while True:
    # Affichage des options
    print("Menu principal :")
    print("1 - Collecter des items RSS")
    print("2 - Effectuer une recherche")
    print("3 - Gérer la classification")
    print("4 - Afficher les statistiques de la base de données")
    print("5 - Quitter l'application")
    n_menu = input("Veuillez choisir le chiffre correspondant à votre choix : ")
    while n_menu not in list_menu:
        n_menu = input("Saisie incorrecte, veuillez choisir le chiffre correspondant à votre choix : ")
    print("")

    if n_menu == list_menu[0]:
        # Collecter des items RSS
        rss_parser = RSSParser("../config/RSS_urls_list.txt")
        rss_parser.start_parsing(es_manager)
    if n_menu == list_menu[1]:
        # Effectuer une recherche
        ask_query(es_manager)
    if n_menu == list_menu[2]:
        # Gérer la classification
        ask_classification(es_manager)
    if n_menu == list_menu[3]:
        # Afficher stats
        es_manager.get_stats()
    if n_menu == list_menu[4]:
        print("Au revoir !")
        quit()