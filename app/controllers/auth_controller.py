from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.auth import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

templates = Jinja2Templates(directory="app/templates")


# Rota de cadastro
@router.get("/cadastro")
def tela_cadastro(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/cadastro.html",
        {"request": request}
    )

# Exibir tela de login
@router.get("/login")
def tela_login(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {"request": request}
    )

# Criar o usuario no banco - cadastrar usuario
@router.post("/cadastro")
def cadastrar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db),
):
    

    #Verificar se o e-mail está cadastrado
    usuario_existente = db.query(Usuario).filter_by(email=email).first()

    if usuario_existente:
        #Retorna o formulario com mensagem de erro
        return templates.TemplateResponse(
            request,
            "auth/cadastro.html",
            {"request": request, "erro": "Este e-mail já está cadastrado"}
        )
    #Criar o novo usuario com senha hash
    novo_usuario = Usuario(nome=nome, email=email, senha_hash=hash_senha(senha))  #Nunca salva a senha pura no db

    db.add(novo_usuario)
    db.commit()

    # Redirecionar para login após cadastro
    return  RedirectResponse(url="/auth/login?cadastro=ok",status_code=302)

# Rota de login
@router.post("/login")
def fazer_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db),
):
    # Buscar o usuário no banco pelo e-mail
    usuario = db.query(Usuario).filter_by(email=email).first()

    #Verificar a senha com brcypt
    senha_correta = ( usuario is not None and verificar_senha(senha, usuario.senha_hash) )

    if not senha_correta:
        #Retorna o formulario com mensagem de erro
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"request": request, "erro": "E-mail ou senha incorretos"}
        )
    
    if not usuario.ativo:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"request": request, "erro": "Usuário inativo. Contate o administrador."}
        )


    # Gerar o token JWT
    # Dados do payload
    token_data = {
        "sub": usuario.email,
        "nome": usuario.nome,
        "role": usuario.role,
        "id": usuario.id
    }

    token = criar_token(token_data)

    #Salvar o token em cookies HttpOnly
    #Redirecionar para a pagina principal
    response = RedirectResponse(url="/", status_code=302)

    response.set_cookie(
        key="acess_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response

