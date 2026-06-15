import socket

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

HOST = "127.0.0.1"
PORT = 8080

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp.connect((HOST, PORT))

requisicao = (
    "GET /arquivo HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    "\r\n"
)

tcp.send(requisicao.encode())

# Recebe cabeçalho HTTP

cabecalho = b""

while b"\r\n\r\n" not in cabecalho:
    cabecalho += tcp.recv(1)

print(cabecalho.decode())

# Recebe chave pública

tam_pub = int.from_bytes(
    tcp.recv(4),
    "big"
)

public_key_data = b""

while len(public_key_data) < tam_pub:
    public_key_data += tcp.recv(4096)

# Recebe assinatura

tam_ass = int.from_bytes(
    tcp.recv(4),
    "big"
)

assinatura = b""

while len(assinatura) < tam_ass:
    assinatura += tcp.recv(4096)

# Recebe arquivo

tam_arq = int.from_bytes(
    tcp.recv(8),
    "big"
)

arquivo = b""

while len(arquivo) < tam_arq:
    arquivo += tcp.recv(4096)

tcp.close()

with open("arquivo_baixado.txt", "wb") as f:
    f.write(arquivo)

print("Arquivo salvo em arquivo_baixado.txt")

public_key = serialization.load_pem_public_key(
    public_key_data
)

# TESTE DE ADULTERAÇÃO
# arquivo += b"X"

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

    print("\n✓ Assinatura válida")
    print("✓ Arquivo autêntico")

except Exception:

    print("\n✗ Assinatura inválida")
    print("✗ Arquivo foi alterado")