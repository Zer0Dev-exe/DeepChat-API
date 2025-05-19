# auth.py
from fastapi import Header, HTTPException, Depends
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def verificar_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de autorización inválido")

    token = authorization.split(" ")[1]
    if token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")
