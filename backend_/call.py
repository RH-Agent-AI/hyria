from fastapi import APIRouter, Query, HTTPException, UploadFile, File
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
# GET - Récupérer les enregistrements de call
# -----------------------------------------------------------------------------
@router.get("/call", tags=["Call"])
def read_calls(
    id: Optional[str] = Query(None, description="Filter by ID"),
    application_id: Optional[str] = Query(None, description="Filter by Application_id"),
    summary: Optional[str] = Query(None, description="Filter by Summary"),
    phone_number: Optional[str] = Query(None, description="Filter by Phone_number"),
    candidats_id: Optional[str] = Query(None, description="Filter by Candidats_id"),
    scoring: Optional[str] = Query(None, description="Filter by Scoring"),
    transcript: Optional[str] = Query(None, description="Filter by Transcript")
):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM call WHERE 1=1"
    params = []
    if id:
        query += " AND ID = %s"
        params.append(id)
    if application_id:
        query += " AND Application_id = %s"
        params.append(application_id)
    if summary:
        query += " AND Summary = %s"
        params.append(summary)
    if phone_number:
        query += " AND Phone_number = %s"
        params.append(phone_number)
    if candidats_id:
        query += " AND Candidats_id = %s"
        params.append(candidats_id)
    if scoring:
        query += " AND Scoring = %s"
        params.append(scoring)
    if transcript:
        query += " AND Transcript = %s"
        params.append(transcript)
    
    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        # Omettre le champ Voice pour éviter les problèmes de sérialisation
        if "Voice" in row_dict:
            row_dict.pop("Voice")
        result.append(row_dict)
    cur.close()
    conn.close()
    return {"data": result}

# -----------------------------------------------------------------------------
# Modèle Pydantic pour la création d'un call
# -----------------------------------------------------------------------------
class CallCreate(BaseModel):
    application_id: Optional[str] = None
    summary: Optional[str] = None
    phone_number: Optional[str] = None
    candidats_id: Optional[str] = None
    scoring: Optional[str] = None
    transcript: Optional[str] = None

# -----------------------------------------------------------------------------
# POST - Créer un enregistrement call
# -----------------------------------------------------------------------------
@router.post("/call", tags=["Call"])
def create_call(
    call: CallCreate,
    voice: Optional[UploadFile] = File(None)
):
    voice_data = voice.file.read() if voice else None

    conn = get_db_connection()
    cur = conn.cursor()
    insert_query = """
    INSERT INTO call (
        Application_id,
        Voice,
        Summary,
        Phone_number,
        Candidats_id,
        Scoring,
        Transcript
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING ID;
    """
    params = (
        call.application_id,
        psycopg2.Binary(voice_data) if voice_data else None,
        call.summary,
        call.phone_number,
        call.candidats_id,
        call.scoring,
        call.transcript
    )
    cur.execute(insert_query, params)
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Call created successfully", "id": new_id}

# -----------------------------------------------------------------------------
# Modèle Pydantic pour la mise à jour d'un call
# -----------------------------------------------------------------------------
class CallUpdate(BaseModel):
    application_id: Optional[str] = None
    summary: Optional[str] = None
    phone_number: Optional[str] = None
    candidats_id: Optional[str] = None
    scoring: Optional[str] = None
    transcript: Optional[str] = None

# -----------------------------------------------------------------------------
# PUT - Mettre à jour un enregistrement call
# -----------------------------------------------------------------------------
@router.put("/call", tags=["Call"])
def update_call(
    call: CallUpdate,
    id: str = Query(..., description="ID du call à mettre à jour")
):
    update_fields = []
    update_params = []
    if call.application_id is not None:
        update_fields.append("Application_id = %s")
        update_params.append(call.application_id)
    if call.summary is not None:
        update_fields.append("Summary = %s")
        update_params.append(call.summary)
    if call.phone_number is not None:
        update_fields.append("Phone_number = %s")
        update_params.append(call.phone_number)
    if call.candidats_id is not None:
        update_fields.append("Candidats_id = %s")
        update_params.append(call.candidats_id)
    if call.scoring is not None:
        update_fields.append("Scoring = %s")
        update_params.append(call.scoring)
    if call.transcript is not None:
        update_fields.append("Transcript = %s")
        update_params.append(call.transcript)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour n'a été fourni.")
    
    query = "UPDATE call SET " + ", ".join(update_fields) + " WHERE ID = %s"
    update_params.append(id)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, update_params)
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucun call trouvé avec cet ID.")
    return {"message": f"Mis à jour {rowcount} call(s) avec succès."}

# -----------------------------------------------------------------------------
# DELETE - Supprimer un enregistrement call
# -----------------------------------------------------------------------------
@router.delete("/call", tags=["Call"])
def delete_call(id: str = Query(..., description="ID du call à supprimer")):
    conn = get_db_connection()
    cur = conn.cursor()
    delete_query = "DELETE FROM call WHERE ID = %s"
    cur.execute(delete_query, (id,))
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Aucun call trouvé avec cet ID.")
    return {"message": "Call deleted successfully", "deleted_count": rowcount}
