from fastapi import APIRouter

from app.api.endpoints import (
    accidentes,
    admin,
    auth,
    auxilio,
    citas,
    clima,
    gruas,
    ia,
    servicios,
    trafico,
    usuarios,
    vehiculos,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(vehiculos.router)
api_router.include_router(servicios.router)
api_router.include_router(gruas.router)
api_router.include_router(citas.router)
api_router.include_router(clima.router)
api_router.include_router(accidentes.router)
api_router.include_router(trafico.router)
api_router.include_router(ia.router)
api_router.include_router(auxilio.router)
api_router.include_router(admin.router)