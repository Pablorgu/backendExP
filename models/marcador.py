from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId
from models.baseMongo import MongoBase


class MarcadorId(BaseModel, MongoBase):
    idMapa: PydanticObjectId

class MarcadorFilter(BaseModel, MongoBase):
    lat: Optional[str] = None
    lon: Optional[str] = None
    email: Optional[str] = None
    imagen: Optional[str] = None

    @field_validator("email")
    def make_regex(cls, v):
        if v is not None:
            return {"$regex": v, "$options": "i"}  # Convertir en regex si no es None
        return v


class Marcador(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    lat: str
    lon: str
    email: str
    imagen: str


class MarcadorNew(BaseModel, MongoBase):
    lat: str
    lon: str
    email: str
    imagen: str

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

    @field_validator("imagen", mode="before")
    def validate_imagen(cls, v):
        if v is not None and not v.startswith("http"):
            raise ValueError("La imagen debe ser una URL válida.")
        return v

class MarcadorUpdate(BaseModel, MongoBase):
    lat: Optional[str] = None
    lon: Optional[str] = None
    email: Optional[str] = None
    imagen: Optional[str] = None


class MarcadorList(BaseModel):
    marcadores: List[Marcador]
