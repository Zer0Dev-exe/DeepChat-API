from pydantic import BaseModel
import re
import unicodedata

class Pregunta(BaseModel):
    pregunta: str

def normalize_text(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = text.replace("ñ", "n")
    return text
