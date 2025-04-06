from fastapi import APIRouter, Query, HTTPException
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )

@router.get("/candidate_info", tags=["Candidate Info"])
def get_candidate_info(phone: str = Query(..., description="Le numéro de téléphone du candidat")):
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Récupérer le candidat par numéro de téléphone
    cur.execute("SELECT * FROM Candidats WHERE Phone = %s", (phone,))
    candidat_row = cur.fetchone()
    if not candidat_row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Aucun candidat trouvé pour ce numéro de téléphone.")

    # PostgreSQL renvoie par défaut les noms de colonnes en minuscules
    candidat_columns = [desc[0] for desc in cur.description]
    candidat = dict(zip(candidat_columns, candidat_row))
    # Convertir l'ID en chaîne de caractères pour l'utiliser dans la jointure
    candidate_id = str(candidat["id"])

    # Extraire la valeur de la colonne CV_text
    cv_text = candidat.get("cv_text")

    # 2. Récupérer toutes les applications du candidat
    cur.execute("SELECT * FROM applications WHERE Candidats_id = %s", (candidate_id,))
    applications_rows = cur.fetchall()
    applications_columns = [desc[0] for desc in cur.description]
    applications = [dict(zip(applications_columns, row)) for row in applications_rows]

    # 3. Récupérer les job_descriptions associées via la table applications.
    # On cast la colonne jd.id en texte pour qu'elle puisse être comparée à a.Job_description_id (qui est en texte)
    join_query = """
        SELECT jd.*
        FROM job_description jd
        INNER JOIN applications a ON jd.id::text = a.Job_description_id
        WHERE a.Candidats_id = %s
    """
    cur.execute(join_query, (candidate_id,))
    job_desc_rows = cur.fetchall()
    job_desc_columns = [desc[0] for desc in cur.description]
    job_descriptions = [dict(zip(job_desc_columns, row)) for row in job_desc_rows]

    cur.close()
    conn.close()

    return {
        "candidate": candidat,
        "cv_text": cv_text,
        "applications": applications,
        "job_descriptions": job_descriptions
    }
