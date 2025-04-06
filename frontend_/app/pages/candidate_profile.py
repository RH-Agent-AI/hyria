# --- START OF FILE pages/candidate_profile.py ---

import streamlit as st
import random
import os
import base64
# Importer les fonctions utilitaires
from ui_utils import (
    get_application_by_id,
    get_job_by_id,
    create_progress_circle,          # Pour le score global
    create_gradient_progress_bar     # Pour les critères
)

# --- Fonction pour afficher le PDF (réinitialisée à width=100% de son conteneur) ---
def display_pdf(file_path):
    if not os.path.exists(file_path):
        st.error(f"Fichier PDF introuvable: {file_path}")
        return
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # Modification ici: width="100%" pour remplir la colonne, suppression des marges auto
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf" style="border: 1px solid #ddd;"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors de l'affichage du PDF : {e}")

# --- Page Configuration ---
st.set_page_config(
    page_title="RH IA - Profil Candidat",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Profil du Candidat")

# --- Vérification de l'état ---
if 'selected_application_id' not in st.session_state or st.session_state.selected_application_id is None:
    st.warning("Veuillez d'abord sélectionner un candidat depuis la page 'Postes'.")
    st.page_link("postes.py", label="Retourner à la liste des postes", icon="📊")
    st.stop()

# --- Récupérer les données ---
application_id = st.session_state.selected_application_id
application_data = get_application_by_id(application_id)

if not application_data:
    st.error(f"Erreur : Impossible de trouver les données pour l'application ID {application_id}.")
    st.session_state.selected_application_id = None # Réinitialiser
    st.page_link("postes.py", label="Retourner à la liste des postes", icon="📊")
    st.stop()

# --- Extraire les informations ---
job_data = get_job_by_id(application_data.get('job_id'))
job_title = job_data['title'] if job_data else "Poste Inconnu"
candidate_name = application_data.get('candidate_name', 'Nom Inconnu')
overall_score = application_data.get('score', 0) # Score 0 à 1
cv_path = application_data.get('cv_path')
cv_filename = application_data.get('cv_filename', 'CV manquant')

# --- Affichage du Profil ---
st.header(f"{candidate_name}")
st.caption(f"Candidature pour : **{job_title}** | Fichier CV : `{cv_filename}`")
st.divider()

# MODIFICATION ICI: Changement de la répartition des colonnes à [1, 1] (50%/50%)
col1, col2 = st.columns([1, 1]) # Colonne Gauche: Scores & Résumé, Colonne Droite: PDF

with col1:
    st.subheader("Correspondance Globale")
    overall_score_percent = 0
    if isinstance(overall_score, (int, float)) and 0 <= overall_score <= 1:
         overall_score_percent = int(overall_score * 100)
    else:
        st.warning("Score global invalide ou manquant.", icon="⚠️")

    circle_html = create_progress_circle(overall_score_percent, size=150, stroke_width=10)
    st.markdown(circle_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Analyse Détaillée (Scores Aléatoires)")
    criteria = [
        "Expérience Pertinente",
        "Compétences Techniques (Hard Skills)",
        "Formation / Diplômes",
        "Compétences Comportementales (Soft Skills)",
        "Motivation / Intérêt pour le poste",
        "Langues",
    ]

    random.seed(str(application_id))
    criteria_scores = {criterion: random.randint(20, 98) for criterion in criteria}
    random.seed()

    for criterion, score in criteria_scores.items():
        st.markdown(f"**{criterion}**")
        progress_bar_html = create_gradient_progress_bar(score, height=12)
        st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.subheader("Résumé Généré (Simulé)")
    strong_points = [c for c, s in criteria_scores.items() if s > 75]
    weak_points = [c for c, s in criteria_scores.items() if s < 40]

    summary = f"* **{candidate_name}** présente un profil **"
    if overall_score_percent > 70: summary += "très prometteur"
    elif overall_score_percent > 50: summary += "intéressant"
    else: summary += "à évaluer avec attention"
    summary += f"** pour le poste de {job_title} (Score global: {overall_score_percent}%).\n"

    if strong_points:
        summary += f"* Points forts apparents : **{', '.join(strong_points[:2])}**.\n"
    if weak_points:
         summary += f"* Points à vérifier/discuter : **{', '.join(weak_points[:2])}**.\n"

    summary += "* *Analyse basée sur des scores simulés. L'examen du CV et un entretien sont nécessaires pour une évaluation complète.*"
    st.markdown(summary)


with col2:
    st.subheader("Visualisation du CV") # Ce titre sera maintenant dans une colonne plus large
    if cv_path and os.path.exists(cv_path):
        display_pdf(cv_path) # Appel de la fonction (réinitialisée à 100% width)
    elif cv_path:
        st.error(f"Le fichier CV '{cv_filename}' est référencé mais n'a pas été trouvé à l'emplacement attendu : `{cv_path}`. Vérifiez le dossier `cv_uploads`.")
    else:
        st.warning("Aucun fichier CV n'est associé à cette candidature.")


st.divider()
# Bouton pour revenir à la liste des candidats du *même* poste
if st.button("⬅️ Retour aux candidats pour ce poste"):
    st.session_state.selected_application_id = None
    try:
        st.switch_page("postes.py")
    except Exception:
         st.info("Veuillez cliquer sur 'Postes' dans la barre latérale pour revenir à la liste.")
         st.rerun()

# --- END OF FILE pages/candidate_profile.py ---