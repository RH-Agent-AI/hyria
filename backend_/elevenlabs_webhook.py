from fastapi import APIRouter, Request, HTTPException
import time
import hmac
from hashlib import sha256
import logging

router = APIRouter()

# Configuration du logger
logger = logging.getLogger("elevenlabs_webhook")
logging.basicConfig(level=logging.INFO)

# Clé secrète partagée (idéalement stockée dans une variable d'environnement)
SECRET = "wsec_8107a966a46431d461e64d8541889ce64e04d64d439b6dd7fb520b007a0df7cd"

@router.post("/elevenlabs/webhook")
async def elevenlabs_webhook(request: Request):
    """
    Endpoint pour recevoir les webhooks d'ElevenLabs avec vérification de signature HMAC.
    """
    # Récupération du corps de la requête sous forme d'octets
    payload_bytes = await request.body()

    # Récupération de l'en-tête de signature
    signature_header = request.headers.get("elevenlabs-signature")
    if not signature_header:
        logger.error("En-tête 'elevenlabs-signature' manquant")
        raise HTTPException(status_code=401, detail="En-tête de signature manquant")

    # Le format attendu est : t=timestamp,v0=hash
    try:
        parts = signature_header.split(',')
        timestamp = parts[0].split('=')[1]
        received_signature = parts[1].split('=')[1]
    except Exception as e:
        logger.error("Format de l'en-tête de signature invalide: %s", signature_header)
        raise HTTPException(status_code=400, detail="Format de l'en-tête de signature invalide")

    # Vérification du timestamp (tolérance de 30 minutes, soit 1800 secondes)
    current_time = int(time.time())
    if int(timestamp) < current_time - 1800:
        logger.error("Le timestamp de la signature est trop ancien: %s", timestamp)
        raise HTTPException(status_code=401, detail="Timestamp de signature trop ancien")

    # Construction du message à signer : "timestamp.payload"
    payload_str = payload_bytes.decode("utf-8")
    full_payload_to_sign = f"{timestamp}.{payload_str}"

    # Calcul de la signature HMAC avec SHA256
    mac = hmac.new(
        key=SECRET.encode("utf-8"),
        msg=full_payload_to_sign.encode("utf-8"),
        digestmod=sha256,
    )
    computed_digest = mac.hexdigest()

    # Comparaison de la signature reçue avec celle calculée
    if received_signature != computed_digest:
        logger.error(
            "Signature invalide. Signature attendue : %s, reçue : %s",
            computed_digest,
            received_signature,
        )
        raise HTTPException(status_code=401, detail="Signature invalide")

    try:
        # Traitement du payload en JSON après validation de la signature
        payload = await request.json()
        logger.info("Webhook reçu avec succès: %s", payload)
        # Ici, ajoutez le traitement du payload selon vos besoins
        return {"message": "Webhook reçu"}
    except Exception as e:
        logger.error("Erreur lors du traitement du payload: %s", e)
        raise HTTPException(status_code=400, detail="Payload invalide")
