from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId
from models.baseMongo import MongoBase

class ProyeccionId(BaseModel, MongoBase):
    idProyeccion: PydanticObjectId

class ProyeccionFilter(BaseModel, MongoBase):
    nombrePelicula: Optional[str] = None
    nombreSala: Optional[str] = None
    fecha: Optional[str] = None

    @field_validator("nombrePelicula", "nombreSala", mode="before")
    def make_regex(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v
    
    
class Proyeccion(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    nombrePelicula: str
    nombreSala: str
    fecha: str

class ProyeccionNew(BaseModel, MongoBase):
    nombrePelicula: str
    nombreSala: str
    fecha: str

    @field_validator("nombrePelicula", mode="before")
    def validate_nombrePelicula(cls, v):
        if v is not None and len(v) < 1:
            raise ValueError("El nombre de la película no puede estar vacío.")
        return v
    
    @field_validator("nombreSala", mode="before")
    def validate_nombreSala(cls, v):
        if v is not None and len(v) < 1:
            raise ValueError("El nombre de la sala no puede estar vacío.")
        return v
    
class ProyeccionUpdate(BaseModel, MongoBase):
    nombrePelicula: Optional[str] = None
    nombreSala: Optional[str] = None
    fecha: Optional[str] = None

class ProyeccionList(BaseModel):
    proyecciones: List[Proyeccion]