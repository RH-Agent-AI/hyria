# --- START OF FILE postes.py ---

import streamlit as st
import os
# Importer les fonctions depuis le module utilitaire
from ui_utils import create_progress_circle, get_job_by_id

# Configuration de la page
st.set_page_config(
    page_title="RH IA - Postes",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Gestion des Postes")

# --- Assurer l'initialisation ---
if 'jobs' not in st.session_state:
    st.error("Erreur: Données des postes non initialisées. Veuillez d'abord visiter la page d'Accueil.")
    st.page_link("acceuil.py", label="Retour à l'accueil", icon="🏠")
    st.stop()
if 'applications' not in st.session_state:
    st.session_state['applications'] = []
if 'selected_job_id' not in st.session_state:
    st.session_state['selected_job_id'] = None
if 'selected_application_id' not in st.session_state:
    st.session_state['selected_application_id'] = None # S'assurer qu'il existe

# --- Fonctions Utilitaires (maintenant dans ui_utils, sauf celle-ci) ---
def get_applications_for_job(job_id):
    """Récupère et trie les candidatures pour un poste spécifique."""
    job_applications = [
        app for app in st.session_state.applications
        if app.get('job_id') == job_id
    ]
    # Tri par score décroissant (gérer score manquant ou invalide)
    job_applications.sort(key=lambda x: x.get('score', 0) if isinstance(x.get('score'), (int, float)) else 0, reverse=True)
    return job_applications

# --- Logique d'Affichage ---

# Si aucun poste n'est sélectionné, afficher la liste
if st.session_state.selected_job_id is None:
    st.header("Postes Ouverts")
    if not st.session_state.jobs:
        st.warning("Aucun poste défini pour le moment.")
    else:
        num_cols = min(len(st.session_state.jobs), 3) # Max 3 colonnes
        job_iter = iter(st.session_state.jobs)
        # Calcule le nombre de lignes nécessaires
        num_rows = (len(st.session_state.jobs) + num_cols - 1) // num_cols

        for r in range(num_rows):
            cols = st.columns(num_cols)
            for i in range(num_cols):
                try:
                    job = next(job_iter)
                    with cols[i]:
                        with st.container(border=True, height=250): # Hauteur fixe pour alignement
                            st.subheader(job['title'])
                            st.caption(f"📍 {job['location']}")
                            st.write(job['description'][:100] + "...")
                            # Utiliser un spacer pour pousser le bouton vers le bas
                            st.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)
                            if st.button("Voir les détails", key=f"details_{job['id']}"):
                                st.session_state.selected_job_id = job['id']
                                st.session_state.selected_application_id = None # Réinitialiser si on change de poste
                                st.rerun()
                except StopIteration:
                     # Si moins de jobs que de colonnes * lignes, laisser vide
                     # cols[i].empty() # Optionnel, pour vider explicitement
                     pass

# Si un poste est sélectionné, afficher ses détails et les candidats
else:
    selected_job = get_job_by_id(st.session_state.selected_job_id)

    if selected_job:
        if st.button("⬅️ Retour à la liste des postes"):
            st.session_state.selected_job_id = None
            st.session_state.selected_application_id = None # Important
            st.rerun()

        st.header(f"Détails du Poste : {selected_job['title']}")
        st.caption(f"📍 {selected_job['location']} | 💰 {selected_job.get('salary', 'N/A')}")

        tab1, tab2 = st.tabs(["📄 Description", "👥 Candidats"])

        with tab1:
            st.subheader("Description Complète")
            st.markdown(selected_job['description'])
            st.subheader("Prérequis")
            st.markdown(selected_job['requirements'])

        with tab2:
            st.subheader("Candidats Ayant Postulé")
            job_applications = get_applications_for_job(st.session_state.selected_job_id)

            if not job_applications:
                st.info("Aucun candidat n'a postulé à ce poste pour le moment.")
            else:
                st.write(f"{len(job_applications)} candidat(s) trouvé(s), classé(s) par score :")

                col_widths = [1.5, 3, 2, 1.5] # Score, Nom, CV, Action
                item_size = 65
                item_height = item_size

                # --- Ligne d'en-tête ---
                header_cols = st.columns(col_widths)
                header_cols[0].caption("**Score**")
                header_cols[1].markdown('<div style="padding-left: 10px;"><span style="font-size: 0.85rem; font-weight: bold; color: #555;">Candidat</span></div>', unsafe_allow_html=True)
                header_cols[2].caption("**CV**")
                header_cols[3].caption("**Action**")
                st.markdown("<hr style='margin: 2px 0 8px 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

                # Itérer sur les candidatures
                for i, app in enumerate(job_applications):
                    cols = st.columns(col_widths)

                    application_id = app.get('application_id', f'missing_id_{i}')
                    candidate_name = app.get('candidate_name', f'Candidat Inconnu {i}')
                    phone_number = app.get('phone_number', 'N/A')
                    cv_filename = app.get('cv_filename', 'CV Manquant')
                    score_value = app.get('score') # De 0 à 1

                    svg_circle = None
                    score_percentage = None
                    score_display = "N/A" # Placeholder texte

                    # Calcul et validation du score pour le cercle
                    if isinstance(score_value, (int, float)) and 0 <= score_value <= 1:
                        try:
                            score_percentage = int(score_value * 100)
                            svg_circle = create_progress_circle(score_percentage, size=item_size, stroke_width=5)
                            score_display = f"{score_percentage}%" # Utile si SVG échoue
                        except Exception as e_svg:
                            st.warning(f"Erreur SVG pour {candidate_name}: {e_svg}", icon="⚠️")
                            svg_circle = None # S'assurer que c'est None
                            score_display = "Err SVG"
                    elif score_value is not None:
                        score_display = "Inv." # Score invalide

                    # --- Colonne 1: Score ---
                    with cols[0]:
                        content_html = ""
                        if svg_circle:
                            content_html = f"<div style='display: flex; align-items: center; justify-content: center; height: {item_height}px;'>{svg_circle}</div>"
                        else:
                            # Placeholder si pas de cercle (score N/A, invalide, ou erreur SVG)
                            content_html = f"""
                            <div style="display: flex; align-items: center; justify-content: center;
                                height: {item_height}px; width: {item_size}px;
                                border: 2px dashed #ccc; border-radius: 50%; font-size: 0.8em;
                                color: grey; font-weight: bold; text-align: center; line-height: 1.2;">
                                {score_display}
                            </div>"""
                        st.markdown(content_html, unsafe_allow_html=True)

                    # --- Colonne 2: Nom ---
                    with cols[1]:
                        st.markdown(f"""
                        <div style="display: flex; flex-direction: column; justify-content: center; height: {item_height}px; padding-left: 10px;">
                            <span style="font-size: 1.0em;">{candidate_name}</span>
                            <span style="color: #666; font-size: 0.85em;">📱 {phone_number}</span>
                        </div>""", unsafe_allow_html=True)

                    # --- Colonne 3: CV ---
                    with cols[2]:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; height: {item_height}px;">
                            <span style="color: #555; font-size: 0.9em;">📄 {cv_filename}</span>
                        </div>""", unsafe_allow_html=True)

                    # --- Colonne 4: Action (Navigation) ---
                    with cols[3]:
                        st.markdown(f'<div style="display: flex; align-items: center; justify-content: center; height: {item_height}px;">', unsafe_allow_html=True)
                        # Utiliser l'application_id comme clé pour unicité
                        if st.button("Voir Profil", key=f"view_{application_id}", help=f"Voir le profil de {candidate_name}", use_container_width=True):
                            # Définir l'ID de l'application sélectionnée
                            st.session_state.selected_application_id = application_id
                            # Tenter la navigation directe
                            try:
                                # Le chemin doit correspondre au nom du fichier dans le dossier 'pages'
                                st.switch_page("pages/candidate_profile.py")
                            except Exception as e:
                                st.error(f"""
                                    Erreur de navigation automatique vers le profil.
                                    Veuillez cliquer sur 'candidate_profile' dans la barre latérale.
                                    Détail: {e}
                                    *(Assurez-vous d'utiliser Streamlit version 1.27+ pour `st.switch_page`)*
                                    """)
                                # L'état `selected_application_id` est quand même défini,
                                # donc la navigation manuelle via la sidebar fonctionnera.
                        st.markdown('</div>', unsafe_allow_html=True)

                    # --- Séparateur ---
                    st.markdown("<hr style='margin: 5px 0 5px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    else:
        st.error("Erreur : Impossible de trouver les détails du poste sélectionné.")
        st.session_state.selected_job_id = None
        st.session_state.selected_application_id = None # Important aussi
        if st.button("Retour à la liste"):
            st.rerun()

# --- END OF FILE postes.py ---