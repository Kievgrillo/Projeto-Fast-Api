from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/") 
async def home():
    return {"mensagem": "Você acessou a rota padrao de autenticação", "autenticado": False}

@auth_router.post("/")
async def criar_conta(usuario_schema: UsuarioSchema, session = Depends(pegar_sessao)):    
    Usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if (Usuario):
        raise HTTPException(status_code=400, detail="Email cadastrado")
    else:
        senha_criptografa = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografa, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usario cadastrado com sucesso {usuario_schema.email}"}


