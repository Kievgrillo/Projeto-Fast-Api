from pydantic import BaseModel
from typing import Optional


class UsuarioSchema (BaseModel):
    nome: str
    emai: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True

class PedidoSchema (BaseModel):
    id_usuario: int

    class Config:
        from_atributes = True

class LoginSchema (BaseModel):
    email: str
    senha: str

    class Config:
        from_atributes = True