import bcrypt

def gerar_hash_senha(senha: str) -> bytes:
    return bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    )

print(gerar_hash_senha("arthu123454321"))