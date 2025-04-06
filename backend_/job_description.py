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
# GET - Récupérer les enregistrements de job_description
# -----------------------------------------------------------------------------
@router.get("/job_description", tags=["Job Description"])
def read_job_descriptions(
    id: Optional[str] = Query(None, description="Filter by ID"),
    name: Optional[str] = Query(None, description="Filter by Name"),
    description: Optional[str] = Query(None, description="Filter by Description")
):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM job_description WHERE 1=1"
    params = []
    if id:
        query += " AND ID = %s"
        params.append(id)
    if name:
        query += " AND Name = %s"
        params.append(name)
    if description:
        query += " AND Description = %s"
        params.append(description)
    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return {"data": result}

# -----------------------------------------------------------------------------
# Modèle Pydantic pour la création d'un job_description
# -----------------------------------------------------------------------------
class JobDescriptionCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# -----------------------------------------------------------------------------
# POST - Créer un enregistrement job_description
# -----------------------------------------------------------------------------
@router.post("/job_description", tags=["Job Description"])
def create_job_description(job: JobDescriptionCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    insert_query = """
    INSERT INTO job_description (Name, Description)
    VALUES (%s, %s)
    RETURNING ID;
    """
    params = (job.name, job.description)
    cur.execute(insert_query, params)
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Job Description created successfully", "id": new_id}

# -----------------------------------------------------------------------------
# Modèle Pydantic pour la mise à jour d'un job_description
# -----------------------------------------------------------------------------
class JobDescriptionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# -----------------------------------------------------------------------------
# PUT - Mettre à jour un enregistrement job_description
# -----------------------------------------------------------------------------
@router.put("/job_description", tags=["Job Description"])
def update_job_description(
    job: JobDescriptionUpdate,
    id: str = Query(..., description="ID du job_description à mettre à jour")
):
    update_fields = []
    update_params = []
    if job.name is not None:
        update_fields.append("Name = %s")
        update_params.append(job.name)
    if job.description is not None:
        update_fields.append("Description = %s")
        update_params.append(job.description)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour n'a été fourni.")
    
    query = "UPDATE job_description SET " + ", ".join(update_fields) + " WHERE ID = %s"
    update_params.append(id)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, update_params)
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucun job_description trouvé avec cet ID.")
    return {"message": f"Mis à jour {rowcount} job description(s) avec succès."}

# -----------------------------------------------------------------------------
# DELETE - Supprimer un enregistrement job_description
# -----------------------------------------------------------------------------
@router.delete("/job_description", tags=["Job Description"])
def delete_job_description(id: str = Query(..., description="ID du job_description à supprimer")):
    conn = get_db_connection()
    cur = conn.cursor()
    delete_query = "DELETE FROM job_description WHERE ID = %s"
    cur.execute(delete_query, (id,))
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucun job_description trouvé avec cet ID.")
    return {"message": "Job Description deleted successfully", "deleted_count": rowcount}
