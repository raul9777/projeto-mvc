from app.database import Session, engine, Base
from app.models.usuario import Usuario
from app.auth import hash_senha


Usuarios = [
    {
        "nome": "Admin",
        "email": "admin@teste.com",
        "senha_hash": "admin123",
        "role": "admin"
    },
    {
        "nome": "Raul",
        "email": "raul@teste.com",
        "senha_hash": "raul123",
        "role": "admin"
    },
]

def criar_usuario():
    db = Session()
    try:
        for usuario in Usuarios:
            existente = db.query(Usuario).filter_by(email=usuario["email"]).first()

            if existente:
                print(f"Já existe esse email: {usuario['email']} no banco")
                continue
            else:
                novo_usuario = Usuario(
                    nome=usuario["nome"],
                    email=usuario["email"],
                    senha_hash=hash_senha(usuario["senha_hash"]),
                    role=usuario["role"],
                )
                db.add(novo_usuario)
        db.commit()
        print(f"Usuários cadastrados com sucesso.")
        
    except Exception as erro:
        db.rollback()
        print(erro)
    finally:
        db.close()

#chamar a função
criar_usuario()