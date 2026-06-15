import socket

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

HOST = "127.0.0.1"
PORT = 8080


def recv_all(sock, size):
    """
    Recebe exatamente 'size' bytes.
    """

    data = b''

    while len(data) < size:

        pacote = sock.recv(size - len(data))

        if not pacote:
            raise ConnectionError("Conexão encerrada")

        data += pacote

    return data


def receber_bloco(sock):
    """
    Recebe:
    [4 bytes tamanho][dados]
    """

    tamanho = int.from_bytes(
        recv_all(sock, 4),
        "big"
    )

    return recv_all(sock, tamanho)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

requisicao = (
    "GET /arquivo HTTP/1.1\r\n"
    f"Host: {HOST}\r\n\r\n"
)

client.sendall(requisicao.encode())

# descarta cabeçalho HTTP
cabecalho = client.recv(1024)

# recebe chave pública
public_key_data = receber_bloco(client)

# recebe assinatura
assinatura = receber_bloco(client)

# recebe arquivo
arquivo = receber_bloco(client)

with open("arquivo_recebido.txt", "wb") as f:
    f.write(arquivo)

# Alteração do arquivo
arquivo += b"X"
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

    print("✓ Assinatura válida")
    print("✓ Arquivo autêntico")

except Exception:

    print("✗ Assinatura inválida")
    print("✗ Arquivo alterado")

client.close()