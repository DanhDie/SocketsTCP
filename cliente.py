import socket
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

HOST = '127.0.0.1'
PORT = 8080

# Carrega chave pública
with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

# Cria socket TCP
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((HOST, PORT))

# Envia requisição HTTP
tcp.send(b"GET /arquivo HTTP/1.1\r\nHost: localhost\r\n\r\n")

# Recebe resposta
resposta = tcp.recv(4096)
tcp.close()

# Separa arquivo e assinatura
cabecalho, corpo = resposta.split(b"\r\n\r\n", 1)
arquivo, assinatura = corpo.split(b"\n---ASSINATURA---\n")

# Mostra e salva o download em um arquivo
print("Arquivo recebido:\n", arquivo.decode())
with open("arquivo_baixado.txt", "wb") as f:
    f.write(arquivo)

# Adulteraçao proposital
arquivo = arquivo + b"X"

# Verifica assinatura
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
    print("\n✅ Assinatura válida: arquivo autêntico!")
except Exception:
    print("\n❌ Assinatura inválida: arquivo pode ter sido alterado!")
