from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import io
import PyPDF2
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Client Mistral
client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

# Ajoutez après la définition de 'candidates'
# Base de données en mémoire pour les offres d'emploi
job_offers = {}

# Ajouter quelques offres d'emploi d'exemple
job_offers["dev-fullstack-001"] = {
    "id": "dev-fullstack-001",
    "title": "Développeur Full Stack",
    "company": "TechCorp",
    "description": """Nous recherchons un développeur Full Stack expérimenté pour rejoindre notre équipe.
    
    Responsabilités:
    - Développer des applications web modernes avec React et Node.js
    - Collaborer avec les designers et les product managers
    - Maintenir et améliorer nos infrastructures existantes
    
    Compétences requises:
    - 3+ ans d'expérience en développement web
    - Maîtrise de JavaScript, React, Node.js
    - Expérience avec les bases de données SQL et NoSQL
    - Connaissance des pratiques DevOps
    """,
    "location": "Paris, France",
    "salary_range": "45K-65K€"
}

job_offers["data-scientist-001"] = {
    "id": "data-scientist-001",
    "title": "Data Scientist",
    "company": "DataInsight",
    "description": """Nous cherchons un Data Scientist talentueux pour analyser nos données et créer des modèles prédictifs.
    
    Responsabilités:
    - Analyser de grands ensembles de données
    - Développer des modèles de machine learning
    - Communiquer les résultats à l'équipe de direction
    
    Compétences requises:
    - Master ou PhD en statistiques, informatique ou domaine connexe
    - Expérience avec Python, pandas, scikit-learn
    - Connaissance de SQL et des outils de visualisation
    - Expérience avec le deep learning est un plus
    """,
    "location": "Lyon, France",
    "salary_range": "50K-70K€"
}

@app.get("/job-offers/")
async def get_all_job_offers():
    """Récupérer toutes les offres d'emploi"""
    return list(job_offers.values())

@app.get("/job-offers/{job_id}")
async def get_job_offer(job_id: str):
    """Récupérer une offre d'emploi spécifique"""
    if job_id not in job_offers:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    return job_offers[job_id]

@app.post("/analyze-cv-for-job/{job_id}")
async def analyze_cv_for_job(job_id: str, file: UploadFile = File(...)):
    """Analyser un CV par rapport à une offre d'emploi spécifique"""
    if job_id not in job_offers:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    job = job_offers[job_id]
    
    # Lire le contenu du fichier
    content = await file.read()
    
    # Extraire le texte
    cv_text = extract_text_from_cv(content)
    
    # Prompt avec l'offre d'emploi
    system_prompt = f"""Tu es un expert RH expérimenté spécialisé dans le recrutement tech.
    
    Voici un CV pour un poste de {job['title']} chez {job['company']}. Analyse-le en profondeur par rapport à cette offre d'emploi:
    
    {job['description']}
    
    Fournis:
    1. Une évaluation de l'adéquation entre le profil et le poste
    2. Un score sur 100 points
    3. Une recommandation claire (à contacter ou non)
    4. Les forces et faiblesses du candidat par rapport au poste
    
    Format ton analyse sous forme de JSON structuré pour faciliter le traitement automatique.
    """
    
    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=f"Voici le CV à analyser pour le poste de {job['title']}:\n\n{cv_text}")
    ]
    
    # Appel à l'API Mistral
    response = client.chat(
        model="mistral-medium",
        messages=messages
    )
    
    # Récupérer la réponse
    result = response.messages[0].content
    
    # Essayer de parser en JSON
    try:
        parsed_result = json.loads(result)
    except:
        parsed_result = {"analysis": result}
    
    # Générer ID unique
    candidate_id = str(uuid.uuid4())
    
    # Stocker les données
    candidates[candidate_id] = {
        "id": candidate_id,
        "filename": file.filename,
        "job_position": job['title'],
        "job_id": job_id,
        "upload_date": datetime.now().isoformat(),
        "analysis": parsed_result,
        "raw_cv": cv_text
    }
    
    # Ajouter l'ID à la réponse
    if isinstance(parsed_result, dict):
        parsed_result["id"] = candidate_id
    else:
        parsed_result = {"id": candidate_id, "analysis": parsed_result}
    
    return parsed_result

# Base de données en mémoire
candidates = {}

def extract_text_from_cv(cv_bytes):
    """Extraire le texte d'un CV en format PDF ou texte"""
    try:
        # Essayer de lire comme un PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(cv_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except:
        # Si ce n'est pas un PDF, traiter comme du texte
        return cv_bytes.decode('utf-8')

@app.post("/analyze-cv/")
async def analyze_cv(file: UploadFile = File(...), job_position: str = "Développeur Full Stack"):
    """Analyser un CV avec Mistral sans instructions détaillées"""
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Extraire le texte
        cv_text = extract_text_from_cv(content)
        
        # Prompt général - laisse le modèle comprendre lui-même ce qu'il doit analyser
        system_prompt = f"""Tu es un expert RH expérimenté spécialisé dans le recrutement tech.
        
        Voici un CV pour un poste de {job_position}. Analyse-le en profondeur et fournis:
        
        1. Une évaluation complète du candidat
        2. Un score sur 100 points
        3. Une recommandation claire (à contacter ou non)
        
        Format ton analyse sous forme de JSON structuré pour faciliter le traitement automatique.
        """
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=f"Voici le CV à analyser pour un poste de {job_position}:\n\n{cv_text}")
        ]
        
        # Appel à l'API Mistral
        response = client.chat(
            model="mistral-medium", # Un modèle plus puissant pour une meilleure compréhension autonome
            messages=messages
        )
        
        # Récupérer la réponse
        result = response.messages[0].content
        
        # Essayer de parser en JSON si possible
        try:
            parsed_result = json.loads(result)
        except:
            # Si pas en JSON, utiliser la réponse brute
            parsed_result = {"analysis": result}
        
        # Générer ID unique
        candidate_id = str(uuid.uuid4())
        
        # Stocker les données
        candidates[candidate_id] = {
            "id": candidate_id,
            "filename": file.filename,
            "job_position": job_position,
            "upload_date": datetime.now().isoformat(),
            "analysis": parsed_result,
            "raw_cv": cv_text
        }
        
        # Ajouter l'ID à la réponse
        if isinstance(parsed_result, dict):
            parsed_result["id"] = candidate_id
        else:
            parsed_result = {"id": candidate_id, "analysis": parsed_result}
        
        return parsed_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conduct-call/{candidate_id}")
async def conduct_call(candidate_id: str):
    """Préparer et simuler un appel avec le candidat"""
    if candidate_id not in candidates:
        raise HTTPException(status_code=404, detail="Candidat non trouvé")
    
    candidate = candidates[candidate_id]
    
    system_prompt = """Tu es un agent RH qui prépare et conduit des premiers appels de screening.
    
    Basé sur l'analyse du CV du candidat, génère:
    1. Un script détaillé pour l'appel
    2. Des questions pertinentes à poser
    3. Les points à approfondir pendant l'entretien
    
    Le tout doit être parfaitement adapté au profil du candidat et au poste.
    """
    
    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=f"Prépare un appel pour ce candidat qui postule à un poste de {candidate['job_position']}. Voici l'analyse de son CV:\n\n{json.dumps(candidate['analysis'], ensure_ascii=False)}\n\nVoici le CV brut:\n\n{candidate['raw_cv']}")
    ]
    
    response = client.chat(
        model="mistral-medium",
        messages=messages
    )
    
    call_preparation = response.messages[0].content
    
    # Mettre à jour les données du candidat
    candidate["call_preparation"] = call_preparation
    
    return {"candidate_id": candidate_id, "call_preparation": call_preparation}

@app.get("/candidates/")
async def get_all_candidates():
    """Récupérer tous les candidats"""
    return list(candidates.values())

@app.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Récupérer un candidat spécifique"""
    if candidate_id not in candidates:
        raise HTTPException(status_code=404, detail="Candidat non trouvé")
    
    return candidates[candidate_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)