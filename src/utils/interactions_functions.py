from utils.globals import ATTRIBUTES
from classification.classifiers import Classifiers
from classification.dataset import Dataset
from classification.evaluation import train_classifiers
from classification.evaluation import best_models_metrics
from classification.evaluation import show_models_cv

def ask_query(es_manager):
    """
    Affiche le sous-menu pour effectuer une recherche

    :param es_manager: le manager de l'API ElasticSearch 
    :type es_manager: ElasticSearchManager
    """
    
    print("Sélectionnez une catégorie de recherche parmi les propositions suivantes : ")
    print("----------------------")
    for cat in ATTRIBUTES:
        print(cat)
    print("----------------------")
    
    bad_input = True
    cat = ""
    while bad_input:
        cat = input("Entrez une catégorie (/!\ Attention, sensible à la casse/!\): ")
        for i in ATTRIBUTES:
            if cat == i:
                bad_input = False
        if bad_input:
            print("Votre demande ne correspond à aucune de nos catégories, veuillez réécrire votre recherche.")
    query = input("Entrez votre requête : ")
    query_f = {"match": {cat: query}}

    try:
        es_manager.connect()
    except ValueError as v:
        print(v)
        return
    es_manager.search(query_f)
    es_manager.disconnect()

def ask_classification(es_manager):
    """
    Affiche le sous-menu pour gérer le composant classficiation

    :param es_manager: le manager de l'API ElasticSearch 
    :type es_manager: ElasticSearchManager
    """
    dataset = Dataset()
    X_fr, X_en, y_fr, y_en = dataset.load_vectorization()

    list_sub_menu = ["1","2","3","4","5","6"]
    while True:
        print("** Menu de classification :")
        print("** 1 - Effectuer les cross-validate de chaque modèle testé")
        print("** 2 - Afficher les métriques de chaque modèle entrainé avec les meilleurs hyper-paramètres")
        print("** 3 - Afficher la configuration des classifieurs des articles")
        print("** 4 - Refaire la vectorisation des données")
        print("** 5 - Refaire l'entrainement des classifieurs")
        print("** 6 - Retour au menu principal")
        n_menu = input("** Veuillez choisir le chiffre correspondant à votre choix : ")
        while n_menu not in list_sub_menu:
            n_menu = input("** Saisie incorrecte, veuillez choisir le chiffre correspondant à votre choix : ")
        print("")

        if n_menu == list_sub_menu[0]:
            show_models_cv(X_fr, y_fr, "fr")
            show_models_cv(X_en, y_en, "en")
        if n_menu == list_sub_menu[1]:
            best_models_metrics(X_fr, y_fr, "fr")
            best_models_metrics(X_en, y_en, "en")
        if n_menu == list_sub_menu[2]:
            classifiers = Classifiers()
            print(classifiers)
        if n_menu == list_sub_menu[3]:
            print("*** /!\ ATTENTION /!\ Refaire une vectorisation écrasera l'actuelle.  /!\ ATTENTION /!\ ")
            print("*** /!\ ATTENTION /!\ Assurez-vous d'avoir assez de données dans votre base  /!\ ATTENTION /!\ ")
            print("*** Êtes-vous sûr de votre choix? ")
            print("*** 1 - Oui")
            print("*** 2 - Non")
            choice = input("*** Veuillez choisir le chiffre correspondant à votre choix : ")
            while choice != "1" and choice != "2":
                choice = input("*** Saisie incorrecte, veuillez choisir le chiffre correspondant à votre choix : ")
            if choice == "1":
                dataset.fit_transform_from_corpus(es_manager)
                X_fr, X_en, y_fr, y_en = dataset.load_vectorization()
                print("Re-vectorisation terminée!")
            print("")
        if n_menu == list_sub_menu[4]:
            train_classifiers(X_fr, X_en, y_fr, y_en)
            print("Ré-entrainement terminé!\n")
        if n_menu == list_sub_menu[5]:
            break