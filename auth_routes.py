from fastapi import APIRouter 

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_roiuter.get("/")
async def autenticar():
    return {"mensagem:" "Você acessou a rota padrao de autenticação", "autenticado": False}
