import socket

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

HOST = "127.0.0.1"
PORT = 8080

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

requisicao = (
    "GET /arquivo HTTP/1.1\r\n"
    f"Host: {HOST}\r\n\r\n"
)

client.send(requisicao.encode())

cabecalho = client.recv(1024)

tam_pub = int.from_bytes(client.recv(4), 'big')
public_key_data = client.recv(tam_pub)

tam_ass = int.from_bytes(client.recv(4), 'big')
assinatura = client.recv(tam_ass)

tam_arq = int.from_bytes(client.recv(4), 'big')

arquivo = b''

while len(arquivo) < tam_arq:
    arquivo += client.recv(1024)

with open("arquivo_recebido.txt", "wb") as f:
    f.write(arquivo)

public_key = serialization.load_pem_public_key(
    public_key_data
)

try:
    public_key.verify(
        assinatura,
        arquivo,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    print("Assinatura válida")
    print("Arquivo autêntico")

except Exception:
    print("Assinatura inválida")
    print("Arquivo foi alterado")

client.close()