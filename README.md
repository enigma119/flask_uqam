# NGO Group Website

Un site web moderne pour une organisation non gouvernementale (ONG) développé avec Flask.


## Pour se connecter

**email**: admin@example.com
**mot de passe**: Test1#test1#

## Description

Ce site web est conçu pour faciliter la communication entre l'ONG et ses parties prenantes, permettant aux visiteurs de s'informer sur les activités de l'organisation, faire des dons, et s'engager comme bénévoles.

## Fonctionnalités

- **Page d'accueil** : Présentation des services et de la mission de l'ONG
- **Section Services** : Détail des différents services offerts
- **À propos** : Information sur l'organisation
- **Système de don** : Formulaire pour effectuer des dons
- **Programme de bénévolat** : Inscription des bénévoles potentiels
- **Contact** : Formulaire de contact pour les requêtes
- ***Partie 2: Module:**  Admin*

## Technologies Utilisées

- Flask (Framework Python)
- Bootstrap 5 (Framework CSS)
- HTML - CSS

## Installation

1. Cloner le repository
2. Créer un environnement virtuel :

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Pour Linux/Mac
   .venv\Scripts\activate     # Pour Windows
   ```
3. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```
4. ***Initialiser la base de données***

```
python init_db.py --reset
```

5. Lancer l'application :

   ```bash
   flask --app app.py --debug run
   ```


   ## Pour se connecter

   **email**: admin@example.com
   **mot de passe**: Test1#test1#



Ou se referer  au fichier init_db.py

Structure du Projet

```
ngo_website/
├── db/
│   ├── ngo.db
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── *.html
│   ├── admin*.html
├── app.py
├── database.py
├── init_db.py
├── security.py
├── requirements.txt
└── README.md
```

## Contribution

Ceci est le projet 1 et la partie 2 développé dans le cadre du cours MGL7030-WEB Hiver 2025 à l'UQAM.
Abass  SARR
SARA07349709
Portfolio: [https://gekyume.vercel.app](https://gekyume.vercel.app)
