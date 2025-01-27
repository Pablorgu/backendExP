import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.auth import AuthMiddleware
from services.archivos import archivos_bp
from services.salas import salas_bp
from services.usuarios import usuarios_router
from services.peliculas import peliculas_bp
from services.proyecciones import proyecciones_bp



load_dotenv()

app = FastAPI()

# Registrar los microservicios como BBlueprintsS
app.include_router(salas_bp)
app.include_router(archivos_bp)
app.include_router(usuarios_router)
app.include_router(peliculas_bp)
app.include_router(proyecciones_bp)


app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-ex-p.vercel.app","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ejecutar la aplicación FastAPI
if __name__ == "__main__":
    puerto = os.getenv("PORT") or 8000
    if puerto:
        puerto = int(puerto)
        uvicorn.run("app:app", host="0.0.0.0", port=puerto, reload=True)

# print("Rutas disponibles:")
# for route in app.routes:
#     print(route.path)
