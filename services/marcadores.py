import httpx
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from cachetools import TTLCache

from models.marcador import MarcadorFilter, MarcadorId, Marcador, MarcadorList, MarcadorNew, MarcadorUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB") or ""

marcadores_bp = APIRouter(prefix="/marcadores", tags=["marcadores"])

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
marcadores = db.marcadores

cache = TTLCache(maxsize=100, ttl=3600)

@marcadores_bp.get("/todos")
def get_marcadores(filtro: MarcadorFilter = Depends()):
    filter = filtro.to_mongo_dict(exclude_none=True)
    marcadores_data = marcadores.find(filter)
    return MarcadorList(marcadores=[marcador for marcador in marcadores_data]).model_dump(exclude_none=True)

@marcadores_bp.get("/")
def get_mapas_por_query_o_coords(q: str = None, lat: str = None, lon: str = None):
    if q:
        if q in cache:
            return {"source": "cache", "data": cache[q]}

        with httpx.Client() as client:
            params = {"q": q, "format": "jsonv2", "addressdetails": 1, "limit": 1}
            response = client.get(
                "https://nominatim.openstreetmap.org/search", params=params
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error al consultar Nominatim",
                )

            data = response.json()
            if not data:
                raise HTTPException(
                    status_code=404, detail="No se encontraron resultados"
                )

            cache[q] = data[0]
            return {"source": "nominatim", "data": data[0]}

    elif lat is not None and lon is not None:
        cache_key = f"{lat},{lon}"
        if cache_key in cache:
            return {"source": "cache", "data": cache[cache_key]}

        with httpx.Client() as client:
            params = {"lat": lat, "lon": lon, "format": "jsonv2", "addressdetails": 1}
            response = client.get(
                "https://nominatim.openstreetmap.org/reverse", params=params
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error al consultar Nominatim",
                )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=404, detail="No se encontraron resultados"
                )

            cache[cache_key] = data
            return {"source": "nominatim", "data": data}

    else:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar 'q' para búsqueda o 'lat' y 'lon' para búsqueda inversa",
        )


@marcadores_bp.get("/{id}", response_model=Marcador)
def get_marcador_por_id(id):
    try:
        marcador = marcadores.find_one({"_id": ObjectId(id)})
        if not marcador:
            raise HTTPException(status_code=404, detail="Marcador no encontrado")

        return marcador
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar el marcador: {str(e)}"
        )

@marcadores_bp.post("/")
def create_marcador(marcador: MarcadorNew):
    try:
        marcador_data = marcador.to_mongo_dict(exclude_none=True)
        marcador_id = marcadores.insert_one(marcador_data).inserted_id
        return MarcadorId(idMapa=str(marcador_id))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al crerar el marcador: {str(e)}"
        )


@marcadores_bp.put("/{id}")
def update_marcador(id, marcador: MarcadorUpdate):
    try:
        filter = {"_id": ObjectId(id)}
        marcador_existente = marcadores.find_one(filter)
        if not marcador_existente:
            raise HTTPException(status_code=404, detail="Marcador no encontrado")

        res = marcadores.update_one(filter, {"$set": marcador.to_mongo_dict(exclude_none=True)})

        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="No se pudo actualizar el marcador")

        return {"message": "Marcador actualizado correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al actualizar el marcador: {str(e)}"
        )


@marcadores_bp.delete("/{id}")
def delete_marcador(id):
    try:
        res = marcadores.delete_one({"_id": ObjectId(id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Marcador no encontrado")

        return {"message": f"Marcador con ID {id} eliminado"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al eliminar el marcador: {str(e)}"
        )
