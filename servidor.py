import socket
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

HOST = "127.0.0.1"
PORT = 8080

with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

with open("public_key.pem", "rb") as f:
    public_key_bytes = f.read()

with open("arquivo.txt", "rb") as f:
    arquivo = f.read()

assinatura = private_key.sign(
    arquivo,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print("Servidor aguardando conexão...")

while True:
    cliente, endereco = server.accept()

    print("Cliente conectado:", endereco)

    requisicao = cliente.recv(1024)

    resposta = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/octet-stream\r\n\r\n"
    )

    cliente.sendall(resposta)

    cliente.sendall(len(public_key_bytes).to_bytes(4, 'big'))
    cliente.sendall(public_key_bytes)

    cliente.sendall(len(assinatura).to_bytes(4, 'big'))
    cliente.sendall(assinatura)

    cliente.sendall(len(arquivo).to_bytes(4, 'big'))
    cliente.sendall(arquivo)

    cliente.close()