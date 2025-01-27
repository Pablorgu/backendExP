import httpx
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from cachetools import TTLCache

from models.proyeccion import ProyeccionFilter, ProyeccionId, Proyeccion, ProyeccionList, ProyeccionNew, ProyeccionUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB") or ""

proyecciones_bp = APIRouter(prefix="/proyecciones", tags=["proyecciones"])

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
proyecciones = db.proyecciones

cache = TTLCache(maxsize=100, ttl=3600)

@proyecciones_bp.get("/")
def get_proyecciones(filtro: ProyeccionFilter = Depends()):
    filter = filtro.to_mongo_dict(exclude_none=True)
    proyecciones_data = proyecciones.find(filter)
    return ProyeccionList(proyecciones=[proyeccion for proyeccion in proyecciones_data]).model_dump(exclude_none=True)

@proyecciones_bp.post("/")
def post_proyeccion(proyeccion: ProyeccionNew):
    proyeccion_id = proyecciones.insert_one(proyeccion.dict()).inserted_id
    return {"id": str(proyeccion_id)}