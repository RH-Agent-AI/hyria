# --- START OF FILE ui_utils.py ---
import math
import streamlit as st # Peut être nécessaire si on utilise des éléments st dedans à terme

# --- Fonction pour créer le cercle de progression SVG ---
def create_progress_circle(score_percent, size=60, stroke_width=5, color_map=None):
    """
    Génère une chaîne SVG pour un cercle de progression avec couleur dynamique.
    CORRIGÉ pour éviter l'erreur InvalidCharacterError.
    """
    if color_map is None:
        # Rouge -> Orange/Jaune -> Vert
        color_map = {30: "#e74c3c", 70: "#f39c12", 101: "#2ecc71"}

    progress_color = "#cccccc" # Couleur par défaut
    sorted_thresholds = sorted(color_map.keys())
    for threshold in sorted_thresholds:
        if score_percent < threshold:
            progress_color = color_map[threshold]
            break
    # Si score >= dernier seuil (ex: 70), prend la couleur de 101 (vert)

    radius = (size / 2) - (stroke_width * 2)
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - (score_percent / 100))
    center = size / 2
    font_size = size / 3.5 # Ajuster la taille de la police relative

    # Construire le SVG en joignant des chaînes pour plus de contrôle sur les espaces
    svg_parts = [
        f'<div style="display:flex; justify-content:center; align-items:center; width:{size}px; height:{size}px;">',
        # S'assurer qu'il y a un espace avant width= etc.
        f' <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="transform: rotate(-90deg);">',
        # Cercle de fond
        f'  <circle cx="{center}" cy="{center}" r="{radius}" stroke="#e6e6e6" stroke-width="{stroke_width}" fill="none"/>',
        # Cercle de progression
        f'  <circle cx="{center}" cy="{center}" r="{radius}" stroke="{progress_color}" stroke-width="{stroke_width}" fill="none" stroke-dasharray="{circumference}" stroke-dashoffset="{offset}" stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease-out;"/>',
        # Texte - **La partie critique** - Espace explicite après <text>
        # Et s'assurer que les attributs sont correctement séparés par des espaces
        f'  <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" fill="#333" font-size="{font_size}px" font-weight="bold" transform="rotate(90 {center},{center})">',
        # Contenu du texte
        f'   {score_percent}%',
        # Balise de fermeture
        f'  </text>',
        f' </svg>',
        f'</div>'
    ]

    # Joindre les parties sans supprimer d'espaces importants accidentellement
    final_svg = "".join(svg_parts)

    # DEBUG: Décommentez pour voir le SVG généré dans la console si l'erreur persiste
    # print("--- Generated SVG ---")
    # print(final_svg)
    # print("---------------------")

    return final_svg


# --- Fonction pour créer une barre de progression avec gradient ---
# (Aucun changement nécessaire ici a priori)
def create_gradient_progress_bar(percentage, height=15):
    """
    Génère une barre de progression HTML avec un gradient et le pourcentage affiché.
    """
    color_start = "#e74c3c"
    color_mid = "#f39c12"
    color_end = "#2ecc71"
    gradient_css = f"linear-gradient(to right, {color_start}, {color_mid}, {color_end})"
    percentage = max(0, min(100, percentage))

    bar_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 8px; height: {height}px;">
        <div title="{percentage}%" style="flex-grow: 1; background-color: #e9ecef; border-radius: 5px; height: 100%; overflow: hidden; position: relative;">
            <div style="
                width: {percentage}%;
                height: 100%;
                background: {gradient_css};
                border-radius: 5px;
                transition: width 0.6s ease-in-out;
            "></div>
        </div>
        <div style="width: 45px; text-align: right; padding-left: 10px; font-size: 0.9em; font-weight: 500;">
            {percentage}%
        </div>
    </div>
    """
    return bar_html

# --- Fonctions pour récupérer les données ---
# (Aucun changement nécessaire ici)
def get_application_by_id(application_id):
    if 'applications' in st.session_state:
        for app in st.session_state.applications:
            if app.get('application_id') == application_id:
                return app
    return None

def get_job_by_id(job_id):
    if 'jobs' in st.session_state:
        for job in st.session_state.jobs:
            if job['id'] == job_id:
                return job
    return None
# --- END OF FILE ui_utils.py ---