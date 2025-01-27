from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId
from models.baseMongo import MongoBase

class PeliculaId(BaseModel, MongoBase):
    idPelicula: PydanticObjectId

class PeliculaFilter(BaseModel, MongoBase):
    titulo: Optional[str] = None
    imagen: Optional[str] = None

    @field_validator("titulo")
    def make_regex(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v
    
class Pelicula(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    titulo: str
    imagen: str

class PeliculaNew(BaseModel, MongoBase):
    titulo: str
    imagen: str

    @field_validator("titulo", mode="before")
    def validate_titulo(cls, v):
        if v is not None and len(v) < 1:
            raise ValueError("El título no puede estar vacío.")
        return v
    
    @field_validator("imagen", mode="before")
    def validate_imagen(cls, v):
        if v is not None and not v.startswith("http"):
            raise ValueError("La imagen debe ser una URL válida.")
        return v
    
class PeliculaUpdate(BaseModel, MongoBase):
    titulo: Optional[str] = None
    imagen: Optional[str] = None

class PeliculaList(BaseModel):
    peliculas: List[Pelicula]