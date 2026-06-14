import socket
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

HOST = '127.0.0.1'
PORT = 8080

# Gera chave privada e pública
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Salva chave pública em arquivo para o cliente usar
with open("public_key.pem", "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )

# Arquivo que será servido
with open("dados.txt", "rb") as f:
    conteudo = f.read()

# Assina o conteúdo
assinatura = private_key.sign(
    conteudo,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Cria socket TCP
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind((HOST, PORT))
tcp.listen()

print(f"Servidor HTTP com assinatura digital iniciado em {HOST}:{PORT}")

while True:
    conexao, cliente = tcp.accept()
    print(f"\nConexão realizada por: {cliente}")

    requisicao = conexao.recv(1024).decode()
    print(f"Requisição recebida:\n{requisicao}")

    if "GET /arquivo" in requisicao:
        resposta = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(conteudo)}\r\n"
            f"Connection: close\r\n"
            f"Server: TrabalhoRedes/1.0\r\n"
            f"\r\n"
        ).encode() + conteudo + b"\n---ASSINATURA---\n" + assinatura
    else:
        resposta = b"HTTP/1.1 404 Not Found\r\n\r\nRecurso nao encontrado"

    conexao.send(resposta)
    conexao.close()
