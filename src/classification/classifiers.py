"""
La classe Classifiers permet de classer des articles RSS (en français ou anglais) 
dans les 6 catégories suivantes : art, politique, economie, santé, science, sport

La classification se fait avec 2 modèles de Machine Learning, un pour le français et un autre pour l'anglais
Les modèles sont déjà entrainés et sont chargés à partir d'un fichier pickle.
Pour les ré-entrainer et/ou visualiser leurs évaluations, veuillez accéder au sous-menu correspondant lors de l'exécution du programme
"""
import pickle

class Classifiers:
    def __init__(self):
        """
        Initialiser les classifieurs pour prédire des catégories selon des articles
        Charge les modèles de classification à partir des fichiers pickles
        """
        file_c = open("../config/classifiers", "rb")
        data_c = pickle.load(file_c)
        self.classifier_fr = data_c["classifier_fr"]
        self.classifier_en = data_c["classifier_en"]
        file_c.close()

        file_v = open("../config/vectorizations", "rb")
        data_v = pickle.load(file_v)
        self.vectorizer_fr = data_v["vectorizer_fr"]
        self.vectorizer_en = data_v["vectorizer_en"]
        file_v.close()

    def predict(self, doc, lang):
        """
        Retourne les probabilités, pour chaque catégorie, du contenu d'un article.
        La plus forte probabilité est la catégorie prédite par le modèle.

        :return: la liste des probabilités de chaque catégorie
        :rtype: list
        """
        if lang == "fr":
            x = self.vectorizer_fr.transform([doc]).toarray()
            predicted = self.classifier_fr.predict_proba(x)[0]
            return predicted
        elif lang == "en":
            x = self.vectorizer_en.transform([doc]).toarray()
            predicted = self.classifier_en.predict_proba(x)[0]
            return predicted
    
    def __str__(self):
        """
        Affiche la configuration

        :return: affichage de la configuration
        :rtype: str
        """
        params_fr = self.classifier_fr.get_params()
        params_en = self.classifier_en.get_params()

        lines = ""
        lines += "--- Classifieurs français ---"
        lines += "\nNom modèle : " + self.classifier_fr.__class__.__name__
        lines += "\nParamètres importants :"
        lines += "\nProfondeur max = " + str(params_fr["max_depth"])
        lines += "\nNb estimateurs = " + str(params_fr["n_estimators"])

        lines += "\n\n--- Classifieurs anglais ---"
        lines += "\nNom modèle : " + self.classifier_en.__class__.__name__
        lines += "\nParamètres importants :"
        lines += "\nProfondeur max = " + str(params_en["max_depth"])
        lines += "\nNb estimateurs = " + str(params_en["n_estimators"]) + "\n"

        return lines