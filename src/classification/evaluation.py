"""
Liste de fonctions utiles pour évaluer et entrainer des modèles de Machine Learning
"""

from utils.globals import CATEGORIES, ENCODED_CATEGORIES
import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, LabelBinarizer
from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import roc_curve, auc, RocCurveDisplay, confusion_matrix, ConfusionMatrixDisplay

# Cross validate
def gen_nested_cv(model, X, y, param_grid, inner_splits, outer_splits):
    """
    Effectue une double cross validation imbriquée avec un modèle
    Permet de trouver les meilleurs hyper-paramètres d'un modèle

    :param model: le modèle à tester
    :type model: Estimator
    :param X: données des articles vectorisés
    :type X: list
    :param y: catégorie des articles
    :type y: list
    :param param_grid: la combinaison de paramètres à tester
    :type param_grid: dict
    :param inner_splits: nombre de boucles à effectuer pour une combinaison d'hyper-paramètres
    :type inner_splits: int
    :param outer_splits: nombre de boucles à effectuer pour toutes les combinaisons
    :type outer_splits: int
    :return: les résultats de la cross validation
    :rtype: dict
    """
    inner_cv = StratifiedKFold(n_splits=inner_splits, shuffle=True, random_state=0)
    outer_cv = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=0)

    grid_search = GridSearchCV(model, param_grid, n_jobs=-1, cv=inner_cv)
    return cross_validate(grid_search, X, y, return_estimator=True, cv=outer_cv)

def show_nested_cv(cv, model_name):
    """
    Affiche les meilleurs résultats d'une double cross validate imbriquée

    :param cv: les résultats d'un cross validate
    :type cv:dict
    :return: les résultats sous forme de chaine de caractères
    :rtype: str
    """
    lines = ""
    for i in range(len(cv["estimator"])):
        lines += "\nMeilleur modèle "+ model_name +" itération " + str(i) + ":\n"
        lines += "Paramètres:\n"
        for k,v in cv["estimator"][i].best_params_.items():
            lines += k + " = " + str(v) + "\n"
        lines += "Score: " + str(cv["estimator"][i].best_score_) + "\n"
    return lines

def show_models_cv(X, y, lang):
    """
    Effectue des cross validate sur plusieurs modèles pour déterminer leurs meilleurs hyper-paramètres.
    Modèles testés : KNN, Régression logistique, GNB, Random Forest, CNN
    Affiche les résultats dans la console et les sauvegarde dans un fichier txt

    :param X: données des articles vectorisés
    :type X: list
    :param y: catégorie des articles
    :type y: list
    :param lang: la langue sur laquelle travailler
    :type lang: str
    """
    lines = "---- Début évaluation double cross validate imbriqué des modèles " + lang + " ----\n"

    ## KNN
    knn = KNeighborsClassifier()
    param_grid = {
        "n_neighbors":[1, 3, 5, 10, 30, 50]
    }
    knn_cv = gen_nested_cv(knn, X, y, param_grid, 3, 5)
    knn_s = "--- KNN best params:"
    knn_s += show_nested_cv(knn_cv, "KNN")
    knn_s += "---------------------- \n"
    lines += knn_s
    print(lines)

    ## Log. regression
    log_reg = make_pipeline(StandardScaler(with_mean=False), LogisticRegression())
    param_grid = {
        "logisticregression__max_iter" : [500, 1000, 1500],
        "logisticregression__C" : [1.0, 0.1, 0.01]
    }
    log_reg_cv = gen_nested_cv(log_reg, X, y, param_grid, 3, 5)
    log_reg_s = "--- Log. Regression best params:"
    log_reg_s += show_nested_cv(log_reg_cv, "Log. Reg.")
    log_reg_s += "----------------------\n"
    print(log_reg_s)
    lines += log_reg_s

    ## Bayesien naïf gaussienne
    gnb = GaussianNB()
    gnb_cv = gen_nested_cv(gnb, X, y, {}, 3, 5)
    gnb_s = "--- Gaussian NB best params:"
    gnb_s += show_nested_cv(gnb_cv, "Gaussian NB")
    gnb_s += "----------------------\n"
    print(gnb_s)
    lines += gnb_s

    ## SVM
    lin_svc = make_pipeline(StandardScaler(with_mean=False), LinearSVC())
    param_grid = {
        "linearsvc__loss" : ['hinge','squared_hinge'],
        "linearsvc__dual" : ["auto"],
        "linearsvc__max_iter": [1500, 2000]
    }
    lin_svc_cv = gen_nested_cv(lin_svc, X, y, param_grid, 3, 5)
    lin_svc_s = "--- Linear SVC best params:"
    lin_svc_s += show_nested_cv(lin_svc_cv, "Linear SVC")
    lin_svc_s += "----------------------\n"
    print(lin_svc_s)
    lines += lin_svc_s

    ## Random Forest
    rf = RandomForestClassifier()
    param_grid = {
        "n_estimators" : [50, 100, 150, 200, 300],
        "max_depth" : [None, 20, 50, 100],
        "min_samples_leaf" : [1, 10]
    }
    rf_cv = gen_nested_cv(rf, X, y, param_grid, 3, 5)
    rf_s = "--- Random Forest best params:"
    rf_s += show_nested_cv(rf_cv, "Random Forest")
    rf_s += "----------------------\n"
    print(rf_s)
    lines += rf_s

    lines += "---- Fin évaluation double cross validate imbriqué en " + lang + " ----"
    print(lines)
    path = "../metrics/"+lang+"_models_nested_cv_results.txt"
    with open(path, "w") as f:
        f.write(lines)
    print("show_models_cv : Résultats sauvegardés dans " + path + "\n")


# Metrics
def show_numerics_metrics(model_name, y_true, y_pred):
    """
    Calcul et retourne, sous forme d'affichage, les résultats de métriques numériques.
    Les métriques sont : accuracy, précision, recall, F1

    :param model_name: le nom du modèle évalué
    :type model_name: str
    :param y_true: les labels verité terrain
    :type y_true: list
    :param y_pred: les labels prédits
    :type y_pred: list
    :return: l'affichage des résultats
    :rtype: str
    """
    lines = ""
    lines += "\nMétriques numériques de " + model_name + " DEBUT ----"
    lines += "\nScore accuracy de " + model_name + " = " + str(accuracy_score(y_true, y_pred))
    lines += "\nScore précision de " + model_name + " = " + str(precision_score(y_true, y_pred, average='macro', zero_division=0.0))
    lines += "\nScore recall de " + model_name + " = " + str(recall_score(y_true, y_pred, average='macro', zero_division=0.0))
    lines += "\nScore F1 de " + model_name + " = " + str(f1_score(y_true, y_pred, average='macro', zero_division=0.0))
    lines += "\nMétriques numériques de " + model_name + " FIN  ----\n"
    return lines

def show_graphic_metrics(model_name, lang, y_true, y_pred, encoded_labels, display_labels):
    """
    Créer deux graphiques : la matrice de confusion et la courbe ROC pour une langue donnée.
    Les images sont sauvegardées dans le dossier "metrics/graphics/lang"

    :param model_name: le nom du modèle évalué
    :type model_name: str
    :param lang: le nom de la langue évalué
    :type lang: str
    :param y_true: les labels verité terrain
    :type y_true: list
    :param y_pred: les labels prédits
    :type y_pred: list
    :param encoded_labels: les catégories encodés en chiffre
    :type encoded_labels: list
    :param display_labels: les noms des catégories à afficher sur la matrice de confusion
    :type display_labels: list
    """
    # Confusion matrix
    fig, ax = plt.subplots(figsize=(10,10))
    cm = confusion_matrix(y_true, y_pred, labels=encoded_labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=display_labels)
    disp.plot()

    path = "../metrics/graphics/"+lang+"/"+lang+"_"+model_name+"_confusion_matrix.jpg"
    plt.title("Matrice de confusion sur " + str(len(y_true)) + " prédictions de catégories du " + model_name)
    plt.savefig(path)
    print("show_graphic_metrics : Matrice de confusion sauvegardée dans " + path)

    # ROC Curve
    label_bin = LabelBinarizer().fit(encoded_labels)
    y_onehot_true = label_bin.transform(y_true)
    y_onehot_pred = label_bin.transform(y_pred)
    class_of_interest = 4
    class_id = np.flatnonzero(label_bin.classes_ == class_of_interest)[0]

    fpr, tpr, _ = roc_curve(y_onehot_true[:, class_id], y_onehot_pred[:, class_id])
    roc_auc = auc(fpr, tpr)
    _, ax = plt.subplots(figsize=(10,10))
    disp = RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc)
    disp.plot(ax=ax)

    path = "../metrics/graphics/"+lang+"/"+lang+"_"+model_name+"_roc_curve.jpg"
    plt.title("ROC Curve du " + model_name + " : art vs autre catégories")
    plt.savefig(path)
    print("show_graphic_metrics : Courbe ROC sauvegardée dans " + path)

def best_models_metrics(X, y, lang):
    """
    Evalue et affiche les métriques des modèles à comparer, configurés avec les meilleurs hyper-paramètres selon la langue

    :param X: données des articles vectorisés
    :type X: list
    :param y: catégorie des articles
    :type y: list
    :param lang: le nom de la langue
    :type lang: str
    """
    if len(X) > 0 and len(y) > 0:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)

        print("---- Début affichage métriques modèles " + lang + "----")
        lines = "Taille ensemble de données d'entrainement = " + str(len(y_train)) + "\n"
        lines += "Taille ensemble de données de test = " + str(len(y_test))+ "\n"
        
        if lang == "fr":
            knn = KNeighborsClassifier(50) # Final model with best parameters
            log_reg = make_pipeline(StandardScaler(with_mean=False), LogisticRegression(max_iter=500, C=0.01))
            gnb = GaussianNB()
            lin_svc = lin_svc = make_pipeline(StandardScaler(with_mean=False), LinearSVC(loss="hinge", dual="auto", max_iter=1000))
            rf = RandomForestClassifier(max_depth=None, min_samples_leaf=1, n_estimators=300)
        elif lang == "en":
            knn = KNeighborsClassifier(10)
            log_reg = make_pipeline(StandardScaler(with_mean=False), LogisticRegression(max_iter=500, C=1.0))
            gnb = GaussianNB() 
            lin_svc = make_pipeline(StandardScaler(with_mean=False), LinearSVC(loss="hinge", dual="auto", max_iter=1000))
            rf = RandomForestClassifier(max_depth = None, min_samples_leaf=1, n_estimators=300)
    
        knn.fit(X_train, y_train)
        knn_y_predict = knn.predict(X_test)
        knn_s = show_numerics_metrics("KNN", y_test, knn_y_predict)
        lines += knn_s
        print(lines)
        show_graphic_metrics("KNN", lang, y_test, knn_y_predict, ENCODED_CATEGORIES, CATEGORIES)


        ## Log. Reg.
        log_reg.fit(X_train, y_train)
        log_reg_y_predict = log_reg.predict(X_test)
        log_reg_s = show_numerics_metrics("log_regression", y_test, log_reg_y_predict)
        print(log_reg_s)
        lines += log_reg_s
        show_graphic_metrics("log_regression", lang, y_test, log_reg_y_predict, ENCODED_CATEGORIES, CATEGORIES)


        # GNB
        gnb.fit(X_train, y_train)
        gnb_y_predict = gnb.predict(X_test)
        gnb_s = show_numerics_metrics("GNB", y_test, gnb_y_predict)
        print(gnb_s)
        lines += gnb_s
        show_graphic_metrics("GNB", lang, y_test, gnb_y_predict, ENCODED_CATEGORIES, CATEGORIES)

        # SVC
        lin_svc.fit(X_train, y_train)
        lin_svc_y_predict = lin_svc.predict(X_test)
        lin_svc_s = show_numerics_metrics("SVC", y_test, lin_svc_y_predict)
        print(lin_svc_s)
        lines += lin_svc_s
        show_graphic_metrics("SVC", lang, y_test, lin_svc_y_predict, ENCODED_CATEGORIES, CATEGORIES)

        # RF
        rf.fit(X_train, y_train)
        rf_y_predict = rf.predict(X_test)
        rf_s = show_numerics_metrics("random_forest", y_test, rf_y_predict)
        print(rf_s)
        lines += rf_s
        show_graphic_metrics("random_forest", lang, y_test, rf_y_predict, ENCODED_CATEGORIES, CATEGORIES)

        path = "../metrics/numerics/"+lang+"_models_numerics_metrics.txt"
        with open(path, "w") as f:
            f.write(lines)
        print("\nshow_numerics_metrics : Résultats sauvegardés dans " + path)
        print("---- Fin affichage métriques modèles " + lang + "----\n")

# Train
def train_classifiers(X_fr, X_en, y_fr, y_en):
    """
    Entraine les classifieurs qui ont obtenus les meilleurs métriques (voir best_models_metrics)
    Sauvegarde les modèles dans le fichier "classifiers" du dossier config
    
    :param X_fr: données des articles français vectorisés 
    :type X_fr: list
    :param y_fr: catégorie des articles français
    :type y_fr: list
    :param X_en: données des articles anglais vectorisés
    :type X_en: list
    :param y_en: catégorie des articles anglais
    :type y_en: list
    """
    classifier_fr = RandomForestClassifier(max_depth = None, min_samples_leaf=1, n_estimators=300)
    classifier_fr.fit(X_fr, y_fr)
    classifier_en = RandomForestClassifier(max_depth = None, min_samples_leaf=1, n_estimators=300)
    classifier_en.fit(X_en, y_en)

    with open("../config/classifiers", "wb") as f:
        data = {}
        data["classifier_fr"] = classifier_fr
        data["classifier_en"] = classifier_en
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)