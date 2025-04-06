from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import psycopg2
import os
from dotenv import load_dotenv
from pydantic import BaseModel

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

# -----------------------------------------------------------------------------
# GET - Récupérer les enregistrements d'applications
# -----------------------------------------------------------------------------
@router.get("/applications", tags=["Applications"])
def read_applications(
    id: Optional[str] = Query(None, description="Filter by ID"),
    job_description_id: Optional[str] = Query(None, description="Filter by Job_description_id"),
    candidats_id: Optional[str] = Query(None, description="Filter by Candidats_id"),
    education_summary: Optional[str] = Query(None, description="Filter by Education_summary"),
    education_scoring: Optional[str] = Query(None, description="Filter by Education_scoring"),
    technicals_scoring: Optional[str] = Query(None, description="Filter by Technicals_scoring"),
    technicals_summary: Optional[str] = Query(None, description="Filter by Technicals_summary"),
    experience_scoring: Optional[str] = Query(None, description="Filter by Experience_scoring"),
    experience_summary: Optional[str] = Query(None, description="Filter by Experience_summary"),
    soft_skill_scoring: Optional[str] = Query(None, description="Filter by Soft_skill_scoring"),
    soft_skill_summary: Optional[str] = Query(None, description="Filter by Soft_skill_summary"),
    additionnal_scoring: Optional[str] = Query(None, description="Filter by Additionnal_scoring"),
    additionnal_summary: Optional[str] = Query(None, description="Filter by Additionnal_summary"),
    summary: Optional[str] = Query(None, description="Filter by Summary"),
    total_scoring: Optional[str] = Query(None, description="Filter by Total_scoring")
):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM applications WHERE 1=1"
    params = []
    if id:
        query += " AND ID = %s"
        params.append(id)
    if job_description_id:
        query += " AND Job_description_id = %s"
        params.append(job_description_id)
    if candidats_id:
        query += " AND Candidats_id = %s"
        params.append(candidats_id)
    if education_summary:
        query += " AND Education_summary = %s"
        params.append(education_summary)
    if education_scoring:
        query += " AND Education_scoring = %s"
        params.append(education_scoring)
    if technicals_scoring:
        query += " AND Technicals_scoring = %s"
        params.append(technicals_scoring)
    if technicals_summary:
        query += " AND Technicals_summary = %s"
        params.append(technicals_summary)
    if experience_scoring:
        query += " AND Experience_scoring = %s"
        params.append(experience_scoring)
    if experience_summary:
        query += " AND Experience_summary = %s"
        params.append(experience_summary)
    if soft_skill_scoring:
        query += " AND Soft_skill_scoring = %s"
        params.append(soft_skill_scoring)
    if soft_skill_summary:
        query += " AND Soft_skill_summary = %s"
        params.append(soft_skill_summary)
    if additionnal_scoring:
        query += " AND Additionnal_scoring = %s"
        params.append(additionnal_scoring)
    if additionnal_summary:
        query += " AND Additionnal_summary = %s"
        params.append(additionnal_summary)
    if summary:
        query += " AND Summary = %s"
        params.append(summary)
    if total_scoring:
        query += " AND Total_scoring = %s"
        params.append(total_scoring)
    
    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return {"data": result}

# -----------------------------------------------------------------------------
# Modèle Pydantic pour la création d'une application
# -----------------------------------------------------------------------------
class ApplicationCreate(BaseModel):
    job_description_id: Optional[str] = None
    candidats_id: Optional[str] = None
    education_summary: Optional[str] = None
    education_scoring: Optional[str] = None
    technicals_scoring: Optional[str] = None
    technicals_summary: Optional[str] = None
    experience_scoring: Optional[str] = None
    experience_summary: Optional[str] = None
    soft_skill_scoring: Optional[str] = None
    soft_skill_summary: Optional[str] = None
    additionnal_scoring: Optional[str] = None
    additionnal_summary: Optional[str] = None
    summary: Optional[str] = None
    total_scoring: Optional[str] = None

# -----------------------------------------------------------------------------
# POST - Créer une application
# -----------------------------------------------------------------------------
@router.post("/applications", tags=["Applications"])
def create_application(app: ApplicationCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    insert_query = """
    INSERT INTO applications (
        Job_description_id,
        Candidats_id,
        Education_summary,
        Education_scoring,
        Technicals_scoring,
        Technicals_summary,
        Experience_scoring,
        Experience_summary,
        Soft_skill_scoring,
        Soft_skill_summary,
        Additionnal_scoring,
        Additionnal_summary,
        Summary,
        Total_scoring
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING ID;
    """
    params = (
        app.job_description_id,
        app.candidats_id,
        app.education_summary,
        app.education_scoring,
        app.technicals_scoring,
        app.technicals_summary,
        app.experience_scoring,
        app.experience_summary,
        app.soft_skill_scoring,
        app.soft_skill_summary,
        app.additionnal_scoring,
        app.additionnal_summary,
        app.summary,
        app.total_scoring
    )
    cur.execute(insert_query, params)
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Application created successfully", "id": new_id}

# -----------------------------------------------------------------------------
# Modèle Pydantic pour la mise à jour d'une application
# -----------------------------------------------------------------------------
class ApplicationUpdate(BaseModel):
    job_description_id: Optional[str] = None
    candidats_id: Optional[str] = None
    education_summary: Optional[str] = None
    education_scoring: Optional[str] = None
    technicals_scoring: Optional[str] = None
    technicals_summary: Optional[str] = None
    experience_scoring: Optional[str] = None
    experience_summary: Optional[str] = None
    soft_skill_scoring: Optional[str] = None
    soft_skill_summary: Optional[str] = None
    additionnal_scoring: Optional[str] = None
    additionnal_summary: Optional[str] = None
    summary: Optional[str] = None
    total_scoring: Optional[str] = None

# -----------------------------------------------------------------------------
# PUT - Mettre à jour une application
# -----------------------------------------------------------------------------
@router.put("/applications", tags=["Applications"])
def update_application(
    app: ApplicationUpdate,
    id: str = Query(..., description="ID de l'application à mettre à jour")
):
    update_fields = []
    update_params = []
    if app.job_description_id is not None:
        update_fields.append("Job_description_id = %s")
        update_params.append(app.job_description_id)
    if app.candidats_id is not None:
        update_fields.append("Candidats_id = %s")
        update_params.append(app.candidats_id)
    if app.education_summary is not None:
        update_fields.append("Education_summary = %s")
        update_params.append(app.education_summary)
    if app.education_scoring is not None:
        update_fields.append("Education_scoring = %s")
        update_params.append(app.education_scoring)
    if app.technicals_scoring is not None:
        update_fields.append("Technicals_scoring = %s")
        update_params.append(app.technicals_scoring)
    if app.technicals_summary is not None:
        update_fields.append("Technicals_summary = %s")
        update_params.append(app.technicals_summary)
    if app.experience_scoring is not None:
        update_fields.append("Experience_scoring = %s")
        update_params.append(app.experience_scoring)
    if app.experience_summary is not None:
        update_fields.append("Experience_summary = %s")
        update_params.append(app.experience_summary)
    if app.soft_skill_scoring is not None:
        update_fields.append("Soft_skill_scoring = %s")
        update_params.append(app.soft_skill_scoring)
    if app.soft_skill_summary is not None:
        update_fields.append("Soft_skill_summary = %s")
        update_params.append(app.soft_skill_summary)
    if app.additionnal_scoring is not None:
        update_fields.append("Additionnal_scoring = %s")
        update_params.append(app.additionnal_scoring)
    if app.additionnal_summary is not None:
        update_fields.append("Additionnal_summary = %s")
        update_params.append(app.additionnal_summary)
    if app.summary is not None:
        update_fields.append("Summary = %s")
        update_params.append(app.summary)
    if app.total_scoring is not None:
        update_fields.append("Total_scoring = %s")
        update_params.append(app.total_scoring)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour n'a été fourni.")
    
    query = "UPDATE applications SET " + ", ".join(update_fields) + " WHERE ID = %s"
    update_params.append(id)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, update_params)
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucune application trouvée avec cet ID.")
    return {"message": f"Mis à jour {rowcount} application(s) avec succès."}

# -----------------------------------------------------------------------------
# DELETE - Supprimer une application
# -----------------------------------------------------------------------------
@router.delete("/applications", tags=["Applications"])
def delete_application(id: str = Query(..., description="ID de l'application à supprimer")):
    conn = get_db_connection()
    cur = conn.cursor()
    delete_query = "DELETE FROM applications WHERE ID = %s"
    cur.execute(delete_query, (id,))
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucune application trouvée avec cet ID.")
    return {"message": "Application deleted successfully", "deleted_count": rowcount}
