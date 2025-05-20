from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes.preguntar import router as preguntar_router
from routes.ping import router as ping_router
from auth import verificar_token

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

app.include_router(
    preguntar_router,
    dependencies=[Depends(verificar_token)]
)

app.include_router(
    ping_router,
    dependencies=[Depends(verificar_token)]
)

@app.get("/")
async def root():
    return {"message": "Hola Mundo"}
