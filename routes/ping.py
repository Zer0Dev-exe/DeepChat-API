from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Modelo de respuesta
class Pregunta(BaseModel):
    ping: int

# Carga de API key
api_key = os.getenv("TOKEN")
if not api_key:
    raise RuntimeError("TOKEN no está definido en variables de entorno")

@router.get("/api/ping", response_model=Pregunta)
def obtener_ping():
    inicio = time.time()

    # Preparar solicitud a DeepSeek
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hola"}
        ],
        "max_tokens": 1
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contactar con DeepSeek: {str(e)}")

    fin = time.time()
    ping_ms = int((fin - inicio) * 1000)

    return Pregunta(ping=ping_ms)
