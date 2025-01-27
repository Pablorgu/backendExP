from datetime import datetime
from typing import List, Optional

from models.baseMongo import MongoBase
from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId


class Visita(BaseModel, MongoBase):
    id: PydanticObjectId = Field(alias="_id")
    emailVisitado: str
    email: str
    fecha: datetime
    token: str

class VisitaNew(BaseModel, MongoBase):
    emailVisitado: str
    email: str
    fecha: datetime
    token: str
    

class VisitaUpdate(BaseModel, MongoBase):
    emailVisitado: Optional[str] = None
    email: Optional[str] = None
    fecha: Optional[datetime] = None
    token: Optional[str] = None

class VisitaQuery(BaseModel):
    emailVisitado: Optional[str] = None
    email: Optional[str] = None
    fecha: Optional[datetime] = None
    token: Optional[str] = None

class VisitaList(BaseModel):
    visitas: List[Visita]
