import socket

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

HOST = "127.0.0.1"
PORT = 8080

# Carrega chave privada
with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

# Carrega chave pública
with open("public_key.pem", "rb") as f:
    public_key_bytes = f.read()

# Carrega arquivo
with open("dados.txt", "rb") as f:
    conteudo = f.read()

# Assina arquivo
assinatura = private_key.sign(
    conteudo,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp.bind((HOST, PORT))
tcp.listen()

print(f"Servidor iniciado em {HOST}:{PORT}")

while True:
    conexao, cliente = tcp.accept()

    print(f"\nCliente conectado: {cliente}")

    requisicao = conexao.recv(1024).decode()

    print(requisicao)

    if "GET /arquivo" in requisicao:

        cabecalho = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/octet-stream\r\n"
            "Connection: close\r\n"
            "Server: TrabalhoRedes/1.0\r\n"
            "\r\n"
        ).encode()

        conexao.sendall(cabecalho)

        # envia chave pública
        conexao.sendall(
            len(public_key_bytes).to_bytes(4, "big")
        )

        conexao.sendall(public_key_bytes)

        # envia assinatura
        conexao.sendall(
            len(assinatura).to_bytes(4, "big")
        )

        conexao.sendall(assinatura)

        # envia arquivo
        conexao.sendall(
            len(conteudo).to_bytes(8, "big")
        )

        conexao.sendall(conteudo)

        print("Arquivo enviado.")

    else:

        conexao.sendall(
            b"HTTP/1.1 404 Not Found\r\n\r\n"
        )

    conexao.close()