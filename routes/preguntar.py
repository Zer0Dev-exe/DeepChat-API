from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import os
import re
import requests
import traceback

from models.preguntar import Pregunta, normalize_text

load_dotenv()

router = APIRouter()

api_key = os.getenv("TOKEN")
if not api_key:
    raise RuntimeError("TOKEN no está definido en variables de entorno")

config = {
    "bannedWords": [
        "gore", "18", "porn", "sex", "violenc", "muert", "asesin",
        "sangr", "drog", "crim", "suicid", "tortur",
        "incest", "ped", "bestial", "violaci", "porno"
    ],
    "max_tokens": 150,
    "languageFilter": {
        "requiredSpanishWords": 1
    },
    "emojis": {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "love": "❤️",
        "cohete": "🚀",
        "think": "🤖✨"
    }
}

spanish_words_path = "spanishWords.txt"
try:
    with open(spanish_words_path, "r", encoding="utf-8") as f:
        spanish_words = set(line.strip().lower() for line in f if line.strip())
except FileNotFoundError:
    raise RuntimeError(f"Archivo {spanish_words_path} no encontrado. Asegúrate de que exista.")

def sanitize_mentions(text: str) -> str:
    def replacer(match):
        mention = match.group(0)
        if mention in ["@everyone", "@here"]:
            return mention[1:]
        return match.group(1) or mention
    return re.sub(r"(@everyone|@here|@(\w+))", replacer, text)

def contains_banned_words(text: str) -> bool:
    banned_roots = config["bannedWords"]
    pattern = "|".join(rf"\b{re.escape(root)}\w*\b" for root in banned_roots)
    banned_regex = re.compile(pattern, re.IGNORECASE)
    return bool(banned_regex.search(text))

def is_spanish(text: str) -> bool:
    words = re.findall(r"\b\w+\b", text)
    count = 0
    for w in words:
        norm_word = normalize_text(w)
        if norm_word in spanish_words:
            count += 1
            if count >= config["languageFilter"]["requiredSpanishWords"]:
                return True
    return False

def replace_emojis_with_codes(text: str) -> str:
    for code, emoji in config["emojis"].items():
        text = text.replace(emoji, f":{code}:")
    return text

@router.post("/api/pregunta")
def responder_pregunta(pregunta: Pregunta):
    user_input = sanitize_mentions(pregunta.pregunta)

    if not is_spanish(user_input):
        raise HTTPException(status_code=400, detail="Por favor, haz la pregunta en español.")

    if contains_banned_words(user_input):
        raise HTTPException(status_code=400, detail="No se puede hablar de este tema.")

    lower_input = user_input.lower()

    if re.search(r"(abrir|crear).*(ticket)", lower_input):
        return {"respuesta": "Para abrir un ticket ve a <#ID>. Puedes elegir entre estas 4 opciones:\n1️⃣ Soporte\n2️⃣ Reportes\n3️⃣ Postulaciones\n4️⃣ Sorteos"}

    if re.search(r"(autoroles|roles automáticos|roles de areas|roles de áreas)", lower_input):
        return {"respuesta": "Los autoroles están en <#ID>. Puedes seleccionar roles de áreas disponibles, notificaciones, etc."}

    if re.search(r"(alianzas|afiliaciones|asociaciones|alianza|ally|affy)", lower_input):
        return {"respuesta": "Para alianzas abre un ticket en <#ID> y contacta con el staff. Mientras tanto, los requisitos de alianza están en <#ID>."}

    messages = [
        {"role": "system", "content": "Te llamas Zer0Dev."},
        {"role": "user", "content": replace_emojis_with_codes(user_input)}
    ]

    if re.search(r"servidor", lower_input):
        messages.append({
            "role": "system",
            "content": "Cuando te pregunten sobre el servidor, responde que es Space Gaming, un servidor con más de 3.2k miembros, que cuenta con secciones como Nekotina, Poketwo, Gaming y más, y que es un lugar divertido y amigable para la comunidad."
        })

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": config["max_tokens"]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        status = response.status_code
        detail = {
            400: "400 - Formato inválido: Por favor revisa el formato de la petición.",
            401: "401 - Autenticación fallida: Revisa tu API key.",
            402: "402 - Saldo insuficiente: Verifica el saldo de tu cuenta.",
            422: "422 - Parámetros inválidos en la solicitud.",
            429: "429 - Límite de tasa alcanzado: Estás enviando solicitudes muy rápido.",
            500: "500 - Error en el servidor, intenta más tarde.",
            503: "503 - Servidor saturado, intenta más tarde."
        }.get(status, f"Error {status}: {response.text}")
        raise HTTPException(status_code=status, detail=detail)
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout al conectar con el servicio externo.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

    data = response.json()
    message = data.get("choices", [{}])[0].get("message", {}).get("content", "No hay respuesta.")
    message = sanitize_mentions(message)
    message = replace_emojis_with_codes(message)

    return {"respuesta": message}
