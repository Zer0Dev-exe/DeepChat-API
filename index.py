from fastapi import FastAPI, Depends
from routes.preguntar import router as preguntar_router
from routes.ping import router as ping_router
from auth import verificar_token

app = FastAPI()

app.include_router(
    preguntar_router,
    dependencies=[Depends(verificar_token)]
)

app.include_router(
    ping_router,
    dependencies=[Depends(verificar_token)]
)

#@app.get("/")
#def read_root():
    #return {"Bienvenido a la API de Deekseep de Zer0Dev"}
