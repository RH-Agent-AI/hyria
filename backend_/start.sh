#!/bin/bash
# Optionnel : activer l'environnement virtuel si vous en utilisez un
# source venv/bin/activate

# Lancer l'application FastAPI avec uvicorn sur le port 8000
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
