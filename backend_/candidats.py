import io
from V0 import execute_agent, extract_from_cv
from applications import create_application
from fastapi import APIRouter, Query, HTTPException, File, UploadFile
from typing import Optional
import psycopg2
import psycopg2.extras  # Import pour gérer les données JSON
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader

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
# GET - Retrieve Candidats records
# -----------------------------------------------------------------------------
@router.get("/candidats", tags=["Candidats"])
def read_candidats(
    id: Optional[str] = Query(None, description="Filter by ID"),
    first_name: Optional[str] = Query(None, description="Filter by First_Name"),
    last_name: Optional[str] = Query(None, description="Filter by Last_Name"),
    address: Optional[str] = Query(None, description="Filter by Address"),
    email: Optional[str] = Query(None, description="Filter by Email"),
    phone: Optional[str] = Query(None, description="Filter by Phone")
):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM Candidats WHERE 1=1"
    params = []
    if id:
        query += " AND ID = %s"
        params.append(id)
    if first_name:
        query += " AND First_Name = %s"
        params.append(first_name)
    if last_name:
        query += " AND Last_Name = %s"
        params.append(last_name)
    if address:
        query += " AND Address = %s"
        params.append(address)
    if email:
        query += " AND Email = %s"
        params.append(email)
    if phone:
        query += " AND Phone = %s"
        params.append(phone)
    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return {"data": result}

# -----------------------------------------------------------------------------
# Pydantic model for creating a Candidat
# -----------------------------------------------------------------------------
class CandidatsCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cv_text: Optional[str] = None
    cv_pdf: Optional[str] = None  # Expected as an encoded string (e.g., base64)
    cv_json: Optional[dict] = None  # New field for updating JSON data

# -----------------------------------------------------------------------------
# POST - Create a Candidat record
# -----------------------------------------------------------------------------
@router.post("/candidats", tags=["Candidats"])
def create_candidat(candidat: CandidatsCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    insert_query = """
    INSERT INTO Candidats (First_Name, Last_Name, Address, Email, Phone, CV_text, CV_pdf, CV_json)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING ID;
    """
    cv_text = execute_agent(candidat.cv_text)
    print(cv_text)
    params = (
        candidat.first_name,
        candidat.last_name,
        candidat.address,
        candidat.email,
        candidat.phone,
        cv_text,
        psycopg2.Binary(candidat.cv_pdf.encode("utf-8")) if candidat.cv_pdf else None,
        psycopg2.extras.Json(candidat.cv_json) if candidat.cv_json else None
    )
    cur.execute(insert_query, params)
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Candidat created successfully", "id": new_id}

# -----------------------------------------------------------------------------
# Pydantic model for updating a Candidat
# -----------------------------------------------------------------------------
class CandidatsUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cv_text: Optional[str] = None
    cv_pdf: Optional[str] = None  # Expected as an encoded string (e.g., base64)
    cv_json: Optional[dict] = None  # New field for updating JSON data

# -----------------------------------------------------------------------------
# PUT - Update a Candidat record
# -----------------------------------------------------------------------------
@router.put("/candidats", tags=["Candidats"])
def update_candidat(
    candidat: CandidatsUpdate,
    id: str = Query(..., description="ID of the candidat to update")
):
    update_fields = []
    update_params = []
    if candidat.first_name is not None:
        update_fields.append("First_Name = %s")
        update_params.append(candidat.first_name)
    if candidat.last_name is not None:
        update_fields.append("Last_Name = %s")
        update_params.append(candidat.last_name)
    if candidat.address is not None:
        update_fields.append("Address = %s")
        update_params.append(candidat.address)
    if candidat.email is not None:
        update_fields.append("Email = %s")
        update_params.append(candidat.email)
    if candidat.phone is not None:
        update_fields.append("Phone = %s")
        update_params.append(candidat.phone)
    if candidat.cv_text is not None:
        update_fields.append("CV_text = %s")
        update_params.append(candidat.cv_text)
    if candidat.cv_pdf is not None:
        update_fields.append("CV_pdf = %s")
        update_params.append(psycopg2.Binary(candidat.cv_pdf.encode("utf-8")))
    if candidat.cv_json is not None:
        update_fields.append("CV_json = %s")
        update_params.append(psycopg2.extras.Json(candidat.cv_json))
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    
    query = "UPDATE Candidats SET " + ", ".join(update_fields) + " WHERE ID = %s"
    update_params.append(id)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, update_params)
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="No candidat found with this ID.")
    
    return {"message": f"Successfully updated {rowcount} candidat(s)."}

# -----------------------------------------------------------------------------
# DELETE - Delete a Candidat record
# -----------------------------------------------------------------------------
@router.delete("/candidats", tags=["Candidats"])
def delete_candidat(id: str = Query(..., description="ID of the candidat to delete")):
    conn = get_db_connection()
    cur = conn.cursor()
    delete_query = "DELETE FROM Candidats WHERE ID = %s"
    cur.execute(delete_query, (id,))
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="No candidat found with this ID.")
    return {"message": "Candidat deleted successfully", "deleted_count": rowcount}
