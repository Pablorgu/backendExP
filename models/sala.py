from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId
from models.baseMongo import MongoBase


class SalaId(BaseModel, MongoBase):
    idMapa: PydanticObjectId

class SalaFilter(BaseModel, MongoBase):
    lat: Optional[str] = None
    lon: Optional[str] = None
    email: Optional[str] = None
    nombre: Optional[str] = None

    @field_validator("email")
    def make_regex_email(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v
    
    @field_validator("nombre")
    def make_regex_nombre(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v


class Sala(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    lat: str
    lon: str
    email: str
    nombre: str


class SalaNew(BaseModel, MongoBase):
    lat: str
    lon: str
    email: str
    nombre: str

    @field_validator("lat", "lon", mode="before")
    def validate_coordinates(cls, v):
        if v is not None:
            try:
                val = float(v)
                if not (-90 <= val <= 90):  # Latitud
                    raise ValueError("Latitud debe estar entre -90 y 90.")
                if not (-180 <= val <= 180):  # Longitud
                    raise ValueError("Longitud debe estar entre -180 y 180.")
            except ValueError:
                raise ValueError("Coordenadas deben ser numéricas.")
        return v

    @field_validator("email", mode="before")
    def validate_email(cls, v):
        if v is not None and "@" not in v:
            raise ValueError("Email debe ser válido.")
        return v

class SalaUpdate(BaseModel, MongoBase):
    lat: Optional[str] = None
    lon: Optional[str] = None
    email: Optional[str] = None
    nombre: Optional[str] = None


class SalaList(BaseModel):
    salas: List[Sala]
