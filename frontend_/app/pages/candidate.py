# --- START OF FILE candidate.py ---

import streamlit as st
import random
import os
import uuid # To generate unique IDs
import time # To add timestamp to filenames maybe

# --- Configuration ---
st.set_page_config(
    page_title="RH IA - Candidater",
    page_icon="✍️",
    layout="centered"
)

# --- Dossier pour stocker les CVs ---
CV_UPLOAD_DIR = "cv_uploads"
if not os.path.exists(CV_UPLOAD_DIR):
    os.makedirs(CV_UPLOAD_DIR)

st.title("✍️ Déposer Votre Candidature")

# --- Assurer l'initialisation ---
if 'jobs' not in st.session_state:
    st.error("Erreur: Données des postes non initialisées. Veuillez d'abord visiter la page d'Accueil.")
    st.stop()
if 'applications' not in st.session_state:
    st.session_state['applications'] = [] # Initialisation si besoin

# --- Formulaire de Candidature ---
if not st.session_state.get('jobs', []): # Utiliser .get pour éviter l'erreur si 'jobs' n'existe pas
    st.warning("Aucun poste n'est actuellement ouvert aux candidatures.")
else:
    # Créer une liste de titres de postes pour le selectbox
    job_options = {job['title']: job['id'] for job in st.session_state.jobs}
    job_titles = list(job_options.keys())

    with st.form("application_form", clear_on_submit=True):
        st.subheader("Informations sur la Candidature")

        # Sélection du poste
        selected_job_title = st.selectbox(
            "Choisissez le poste pour lequel vous souhaitez postuler :",
            options=job_titles,
            index=None,
            placeholder="Sélectionner un poste..."
            )

        # Nom du candidat
        candidate_name = st.text_input("Votre Nom et Prénom :")

        # Numéro de téléphone
        phone_number = st.text_input("Votre Numéro de Téléphone :")

        # Téléchargement du CV
        uploaded_cv = st.file_uploader(
            "Téléchargez votre CV (format PDF uniquement) :",
            type="pdf",
            accept_multiple_files=False
            )

        # Bouton de soumission
        submitted = st.form_submit_button("Envoyer ma Candidature")

        # --- Traitement après soumission ---
        if submitted:
            # Validation
            error = False
            if not selected_job_title:
                st.warning("Veuillez sélectionner un poste.")
                error = True
            if not candidate_name:
                st.warning("Veuillez entrer votre nom.")
                error = True
            if uploaded_cv is None:
                st.warning("Veuillez télécharger votre CV.")
                error = True

            if not error:
                # Récupérer l'ID du poste sélectionné
                selected_job_id = job_options[selected_job_title]

                # Générer un score aléatoire pour le MVP
                random_score = random.uniform(0.1, 0.99)

                # Générer un ID unique pour la candidature
                application_id = str(uuid.uuid4())

                # Sauvegarder le fichier CV
                # Utiliser l'ID unique et timestamp pour éviter les collisions
                # et garder une trace de l'original
                original_filename = uploaded_cv.name
                # Nettoyer un peu le nom original pour le chemin (optionnel)
                safe_original_filename = "".join(c for c in original_filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
                unique_filename = f"{application_id}_{int(time.time())}_{safe_original_filename}.pdf"
                cv_save_path = os.path.join(CV_UPLOAD_DIR, unique_filename)

                try:
                    with open(cv_save_path, "wb") as f:
                        f.write(uploaded_cv.getvalue())
                    st.success("Fichier CV sauvegardé avec succès.") # Feedback pour debug/info

                    # Préparer les données de la candidature
                    new_application = {
                        'application_id': application_id, # ID Unique
                        'candidate_name': candidate_name,
                        'phone_number': phone_number,  # Ajout du numéro de téléphone
                        'cv_filename': original_filename, # Nom original pour affichage
                        'cv_path': cv_save_path,       # Chemin vers le fichier sauvegardé
                        'job_id': selected_job_id,
                        'score': random_score
                    }

                    # Ajouter la candidature à la liste dans st.session_state
                    st.session_state.applications.append(new_application)

                    st.success(f"Merci {candidate_name}, votre candidature pour le poste de '{selected_job_title}' a bien été reçue !")
                    st.info(f"Votre CV '{original_filename}' a été enregistré.")
                    st.balloons()

                except Exception as e:
                    st.error(f"Erreur lors de la sauvegarde du CV : {e}")
                    # Optionnel: supprimer le fichier potentiellement corrompu si besoin
                    if os.path.exists(cv_save_path):
                         os.remove(cv_save_path)

# Afficher les candidatures actuelles (pour debug/vérification)
# st.write("Candidatures actuelles:", st.session_state.applications)
# --- END OF FILE candidate.py ---