import os

import requests
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from starlette.middleware.base import BaseHTTPMiddleware

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
MONGO_URL = os.getenv("MONGO_URL")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
         if request.method in ["PUT","DELETE"]:
                if "Authorization" not in request.headers:
                    raise HTTPException(status_code=401, detail="No se proporcionó un token de autorización")

                access_token = request.headers["Authorization"].split(" ")[1]
                url = "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=" + access_token
                response = requests.get(url)

                if response.status_code != 200:
                    raise HTTPException(status_code=401, detail="Error al validar el token de autorización. La api de Google devolvió un error")

                # get sub from token
                token_info = response.json()
                googleId = token_info["sub"]

                # get user info
                client = MongoClient(MONGO_URL)
                db = client.MiMapa
                usuarios = db.usuarios
                user = usuarios.find_one({"googleId": googleId})

                userData = {
                        "access_token": access_token,
                        "googleId": googleId,
                        }
                
                request.state.user = userData

        except HTTPException as e:
            return JSONResponse(status_code=401, content={"detail": f"{e}"})
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": f"Error al validar el token de autorización, {e}"})
        response = await call_next(request)
        return response
