import httpx
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from cachetools import TTLCache

from models.pelicula import PeliculaFilter, PeliculaId, Pelicula, PeliculaList, PeliculaNew, PeliculaUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB") or ""

peliculas_bp = APIRouter(prefix="/peliculas", tags=["peliculas"])

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
peliculas = db.peliculas

cache = TTLCache(maxsize=100, ttl=3600)

@peliculas_bp.get("/")
def get_peliculas(filtro: PeliculaFilter = Depends()):
    filter = filtro.to_mongo_dict(exclude_none=True)
    peliculas_data = peliculas.find(filter)
    return PeliculaList(peliculas=[pelicula for pelicula in peliculas_data]).model_dump(exclude_none=True)

@peliculas_bp.post("/")
def post_pelicula(pelicula: PeliculaNew):
    pelicula_id = peliculas.insert_one(pelicula.dict()).inserted_id
    return {"id": str(pelicula_id)}