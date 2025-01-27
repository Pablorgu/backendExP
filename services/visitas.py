import os

import pymongo
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from models.visita import Visita, VisitaList, VisitaNew, VisitaQuery, VisitaUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB") or ""

visitas_bp = APIRouter(prefix="/visitas", tags=["visitas"])

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
visitas = db.visitas

#Obtener todas las visitas de un usuario por su email
@visitas_bp.get("/{email}")
async def get_visitas(email: str):
    evisitas = visitas.find({"email": email})
    visitas_list = []
    for visita in evisitas:
        visitas_list.append(Visita(**visita))
    return {"eventos": visitas_list}

#Crear una nueva visita
@visitas_bp.post("/")
async def create_visita(visita: VisitaNew):
    visita_dict = visita.dict()
    visita_id = visitas.insert_one(visita_dict).inserted_id
    return {"id": visita_id}