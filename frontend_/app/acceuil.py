import streamlit as st
import random

# Configuration de la page (optionnel mais recommandé)
st.set_page_config(
    page_title="RH IA - Accueil",
    page_icon="👋",
    layout="wide"
)

# --- Initialisation des données (à faire une seule fois) ---
# Utilisation de st.session_state pour conserver les données entre les pages
if 'jobs' not in st.session_state:
    st.session_state['jobs'] = [
        {
            "id": "dev-web-01",
            "title": "Développeur Web Fullstack",
            "location": "Paris, France",
            "description": "Nous recherchons un développeur web fullstack expérimenté (React/Node.js) pour rejoindre notre équipe dynamique. Vous travaillerez sur des projets innovants et contribuerez à l'évolution de notre plateforme.",
            "requirements": "- 3+ ans d'expérience\n- Maîtrise de React, Node.js, Express\n- Connaissance des bases de données SQL et NoSQL\n- Esprit d'équipe et bonnes capacités de communication",
            "salary": "45k€ - 60k€ selon profil"
        },
        {
            "id": "data-sci-01",
            "title": "Data Scientist Junior",
            "location": "Lyon, France (Télétravail partiel possible)",
            "description": "Intégrez notre pôle data et participez à l'analyse de nos données pour en extraire des insights clés. Vous développerez des modèles prédictifs et aiderez à la prise de décision.",
            "requirements": "- Master en Data Science, Statistiques ou domaine lié\n- Maîtrise de Python (Pandas, Scikit-learn)\n- Connaissance des algorithmes de Machine Learning\n- Anglais courant",
            "salary": "38k€ - 45k€"
        },
        {
            "id": "marketing-01",
            "title": "Responsable Marketing Digital",
            "location": "Remote (France)",
            "description": "Définissez et mettez en œuvre notre stratégie marketing digitale. Gérez les campagnes SEO/SEA, les réseaux sociaux et l'emailing pour accroître notre visibilité et générer des leads.",
            "requirements": "- 5+ ans d'expérience en marketing digital\n- Excellente connaissance des outils d'analyse (Google Analytics)\n- Compétences en gestion de projet\n- Créativité et proactivité",
            "salary": "50k€ - 65k€"
        }
    ]

if 'applications' not in st.session_state:
    # Liste pour stocker les candidatures: {'candidate_name': str, 'cv_filename': str, 'job_id': str, 'score': float}
    st.session_state['applications'] = []

if 'selected_job_id' not in st.session_state:
    st.session_state['selected_job_id'] = None # Pour suivre le poste sélectionné dans la page Postes

# --- Contenu de la Page d'Accueil ---
st.title("👋 Bienvenue sur le portail RH IA (MVP)")
st.sidebar.success("Navigation") # Indique la barre de navigation créée par Streamlit

st.markdown("""
Ceci est un prototype (MVP) pour une plateforme de gestion RH assistée par IA.

**Fonctionnalités actuelles :**

*   **📊 Postes :** Visualisation des fiches de postes et des candidats associés (pour la RH).
*   **✍️ Candidater :** Permet aux candidats de postuler en soumettant leur CV.

*Utilisez la barre de navigation à gauche pour accéder aux différentes sections.*
""")

st.info("Note : Les scores de correspondance des candidats sont actuellement générés aléatoirement pour ce MVP.")

# Vous pouvez ajouter plus d'infos ou de graphiques ici si nécessaire