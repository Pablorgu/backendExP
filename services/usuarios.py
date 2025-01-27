import json
import os
from typing import Optional

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from models.user import User, UserList, UserNew
from pymongo import MongoClient

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB") or ""

usuarios_router = APIRouter(prefix="/usuarios", tags=["usuarios"])

# Configuración de MongoDB
client = MongoClient(MONGO_URL)
db = client[MONGO_DB]
usuarios = db.usuarios

# GET /usuarios
@usuarios_router.get("/", response_model=UserList)
def get_users():
    try:
        users_data = usuarios.find().to_list(1000)
        return UserList(users=users_data)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al buscar los usuarios: {str(e)}"
        )

# # POST /usuarios
# @usuarios_router.post("/", response_model=User)
# def create_user(user: UserNew):
#     try:
#         user_dump = user.model_dump()
#         usuario = usuarios.find_one({"googleId": user_dump["googleId"]})
#         if usuario: 
#             return usuario
#         if not usuario:
#             user_id = usuarios.insert_one(user_dump).inserted_id
#             user = usuarios.find_one({"_id": ObjectId(user_id)})
#             return user
#     except Exception as e:
#         raise HTTPException(
#             status_code=400, detail=f"Error al crear el usuario: {str(e)}"
#         )
    
# POST /usuarios/
@usuarios_router.post("/")
async def login_user(userData: UserNew, request: Request):
    try:
        user = usuarios.find_one({"email": userData.email})
        if user:
            usuarios.update_one(
                {"email": userData.email},
                {"$set": {"access_token": userData.access_token, "googleId":userData.googleId, "expires_in":userData.expires_in, "name":userData.name}},
            )
        else:
            usuarios.insert_one(userData.to_mongo_dict(exclude_none=True))

        # return user
        user = usuarios.find_one({"email": userData.email})
        raise HTTPException(status_code=200, detail=User(**user).model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al iniciar sesión: {str(e)}"
        )
