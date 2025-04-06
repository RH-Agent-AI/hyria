# Hyria

Hyria est une application web basée sur **FastAPI** et **Streamlit** destinée à gérer les processus RH, notamment la gestion des candidats et des offres d'emploi. Ce projet a été développé dans le contexte d'un hackathon et intègre des déploiements automatisés via GitHub et AWS.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture du projet](#architecture-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement de l'application](#lancement-de-lapplication)
- [Déploiement sur AWS](#déploiement-sur-aws)
- [Contribuer](#contribuer)
- [Licence](#licence)
- [Contact](#contact)

## Fonctionnalités

- **API REST** : Développée avec FastAPI pour une gestion efficace des requêtes
- **Interface utilisateur** : Interface interactive construite avec Streamlit
- **Gestion des candidats** : Ajout, modification et suivi des candidats
- **Gestion des offres d'emploi** : Création et gestion des descriptions de postes
- **Gestion des candidatures** : Suivi des candidatures aux offres d'emploi
- **Intégration IA** : Utilisation de Mistral AI via Langchain pour l'analyse des CV et des offres
- **Base de données PostgreSQL** : Stockage persistant des données (hébergée sur Render)

## Architecture du projet

Le projet est divisé en deux parties principales :

- **Backend (`backend_/`)** : API REST développée avec FastAPI, gère la logique métier et l'accès à la base de données
- **Frontend (`frontend_/`)** : Interface utilisateur développée avec Streamlit

### Structure du Backend

```
backend_/
├── main.py                 # Point d'entrée de l'application FastAPI
├── candidats.py            # Gestion des candidats
├── job_description.py      # Gestion des descriptions de postes
├── applications.py         # Gestion des candidatures
├── call.py                 # Gestion des appels
├── candidate_info.py       # Informations des candidats
├── elevenlabs_webhook.py   # Webhooks pour ElevenLabs
├── requirements.txt        # Dépendances Python
├── start.sh                # Script de démarrage
└── .env                    # Variables d'environnement
```

### Structure du Frontend

```
frontend_/
├── app/
│   ├── acceuil.py          # Page d'accueil
│   ├── ui_utils.py         # Utilitaires pour l'interface utilisateur
│   │   ├── candidate.py    # Gestion des candidats
│   │   ├── candidate_profile.py # Profil des candidats
│   │   └── postes.py       # Gestion des postes
├── .env                    # Variables d'environnement
```

## Prérequis

- Python 3.8 ou supérieur
- pip
- Virtualenv (recommandé)
- Git
- Compte AWS (pour le déploiement)
- Compte Render (pour la base de données) ou autre fournisseur PostgreSQL

## Installation

1. **Cloner le dépôt**

   ```bash
   git clone https://gitingest.com/RH-Agent-AI/hyria.git
   cd hyria
   ```

2. **Configuration de l'environnement virtuel (recommandé)**

   ```bash
   # Pour Linux/macOS
   python -m venv venv
   source venv/bin/activate

   # Pour Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Installation des dépendances du backend**

   ```bash
   cd backend_
   pip install -r requirements.txt
   ```

4. **Installation des dépendances du frontend**

   ```bash
   cd ../frontend_
   pip install streamlit pandas matplotlib plotly
   ```

## Configuration

1. **Configuration du Backend**

   Créez un fichier `.env` dans le dossier `backend_` avec les variables suivantes :

   ```
   DB_HOST=votre_hote_db
   DB_PORT=5432
   DB_NAME=votre_nom_db
   DB_USER=votre_utilisateur_db
   DB_PASSWORD=votre_mot_de_passe_db
   MISTRAL_API_KEY=votre_cle_api_mistral
   ```

2. **Configuration du Frontend**

   Créez un fichier `.env` dans le dossier `frontend_` avec les variables suivantes :

   ```
   MISTRAL_API_KEY=votre_cle_api_mistral
   DB_NAME=votre_nom_db
   DB_USER=votre_utilisateur_db
   DB_PASSWORD=votre_mot_de_passe_db
   DB_HOST=votre_hote_db
   DB_PORT=5432
   ```

## Lancement de l'application

1. **Démarrer le Backend**

   ```bash
   cd backend_
   bash start.sh
   # Ou sous Windows
   # python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   Le backend sera accessible à l'adresse http://localhost:8000

2. **Démarrer le Frontend**

   ```bash
   cd frontend_
   streamlit run app/acceuil.py
   ```

   Le frontend sera accessible à l'adresse http://localhost:8501

## Déploiement sur AWS

### Prérequis pour le déploiement

- Compte AWS
- AWS CLI configuré
- Permissions IAM appropriées

### Utilisation de RDS pour la base de données

1. **Créer une instance RDS PostgreSQL**

   - Dans la console AWS, allez dans RDS
   - Créez une nouvelle instance de base de données PostgreSQL
   - Configurez les paramètres de sécurité pour permettre l'accès depuis vos services

2. **Mettre à jour les variables d'environnement**

   Mettez à jour les variables d'environnement du backend et du frontend avec les nouvelles informations de connexion à la base de données.

## Contribuer

Pour contribuer au projet, veuillez suivre ces étapes :

1. Fork du dépôt
2. Création d'une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit des modifications (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouverture d'une Pull Request

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Contact

Pour toute question ou demande, veuillez contacter l'équipe RH-Agent-AI.
