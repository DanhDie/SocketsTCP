import socket

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

HOST = "127.0.0.1"
PORT = 8080


def enviar_com_tamanho(sock, dados):
    """
    Envia:
    [4 bytes tamanho][dados]
    """
    sock.sendall(len(dados).to_bytes(4, "big"))
    sock.sendall(dados)


# Carrega chave privada permanente
with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

# Carrega chave pública
with open("public_key.pem", "rb") as f:
    public_key_data = f.read()

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind((HOST, PORT))
tcp.listen()

print(f"Servidor iniciado em {HOST}:{PORT}")

while True:

    conexao, endereco = tcp.accept()

    try:

        print(f"Cliente conectado: {endereco}")

        requisicao = conexao.recv(1024).decode()

        print(requisicao)

        if "GET /arquivo" not in requisicao:
            conexao.sendall(b"ERRO")
            continue

        # Lê arquivo
        with open("dados.txt", "rb") as f:
            arquivo = f.read()

        # Assina conteúdo
        assinatura = private_key.sign(
            arquivo,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Cabeçalho HTTP simples
        conexao.sendall(
            b"HTTP/1.1 200 OK\r\n"
            b"Connection: close\r\n\r\n"
        )

        # Envia chave pública
        enviar_com_tamanho(conexao, public_key_data)

        # Envia assinatura
        enviar_com_tamanho(conexao, assinatura)

        # Envia arquivo
        enviar_com_tamanho(conexao, arquivo)

        print("Arquivo enviado")

    finally:
        conexao.close()