import socket

HOST = '127.0.0.1'
PORT = 5000

# Cria socket TCP
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associa IP e porta
tcp.bind((HOST, PORT))

# Coloca em modo de escuta
tcp.listen()

print(f'Servidor TCP iniciado em {HOST}:{PORT}')

while True:
    # Aceita conexão
    conexao, cliente = tcp.accept()

    print(f'\nConexão realizada por: {cliente}')

    while True:
        mensagem = conexao.recv(1024)

        if not mensagem:
            break

        print(f'\nCliente: {cliente}')
        print(f'Mensagem: {mensagem.decode()}')

    print(f'Finalizando conexão do cliente {cliente}')
    conexao.close()