import httpx
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from cachetools import TTLCache

from models.sala import SalaFilter, SalaId, Sala, SalaList, SalaNew, SalaUpdate

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB") or ""

salas_bp = APIRouter(prefix="/salas", tags=["salas"])

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
salas = db.salas
proyecciones = db.proyecciones
cache = TTLCache(maxsize=100, ttl=3600)

@salas_bp.get("/todos")
def get_salas(filtro: SalaFilter = Depends()):
    filter = filtro.to_mongo_dict(exclude_none=True)
    salas_data = salas.find(filter)
    return SalaList(salas=[sala for sala in salas_data]).model_dump(exclude_none=True)

@salas_bp.get("/")
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


@salas_bp.get("/{id}", response_model=Sala)
def get_sala_por_id(id):
    try:
        sala = salas.find_one({"_id": ObjectId(id)})
        if not sala:
            raise HTTPException(status_code=404, detail="Sala no encontrada")

        return sala
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar la sala: {str(e)}"
        )

@salas_bp.post("/")
def create_sala(sala: SalaNew):
    try:
        sala_data = sala.to_mongo_dict(exclude_none=True)
        sala_id = salas.insert_one(sala_data).inserted_id
        return SalaId(idMapa=str(sala_id))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al crear la sala: {str(e)}"
        )


@salas_bp.put("/{id}")
def update_sala(id, sala: SalaUpdate):
    try:
        filter = {"_id": ObjectId(id)}
        sala_existente = salas.find_one(filter)
        if not sala_existente:
            raise HTTPException(status_code=404, detail="Sala no encontrada")

        res = salas.update_one(filter, {"$set": sala.to_mongo_dict(exclude_none=True)})

        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="No se pudo actualizar la sala")

        return {"message": "Sala actualizada correctamente"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al actualizar la sala: {str(e)}"
        )


@salas_bp.delete("/{id}")
def delete_sala(id):
    try:
        res = salas.delete_one({"_id": ObjectId(id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Sala no encontrada")

        return {"message": f"Sala con ID {id} eliminado"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al eliminar la Sala: {str(e)}"
        )

@salas_bp.get("/peliculas/{nombrePelicula}")
def get_Salas_por_pelicula(nombrePelicula):
    try:
        proyecciones_data = proyecciones.find({"nombrePelicula": nombrePelicula})
        if not proyecciones_data:
            raise HTTPException(status_code=404, detail="No se encontraron salas para la película")

        salas_nombre = [proyeccion["nombreSala"] for proyeccion in proyecciones_data]
        salas = salas.find({"nombre": {"$in": salas_nombre}})
        return SalaList(salas=[sala for sala in salas]).model_dump(exclude_none=True)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar las salas: {str(e)}"
        )