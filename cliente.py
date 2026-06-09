import socket

HOST = '127.0.0.1'
PORT = 5000

# Cria socket TCP
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
tcp.connect((HOST, PORT))

print('\nDigite suas mensagens')
print('Para sair use: EXIT\n')

mensagem = input()

while mensagem != 'EXIT':
    tcp.send(mensagem.encode())
    mensagem = input()

tcp.close()