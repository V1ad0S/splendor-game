import sys, socket


IP = 'localhost'
PORT = 8000

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_SOCKET.bind((IP, PORT))
SERVER_SOCKET.listen()

players = []

print(f'Listening for connections on {IP}:{PORT}...')


def new_connection(client_socket, client_address):
    if len(players) >= 2:
        return False
    # player should send his name
    user = client_socket.recv(1024).decode('utf-8')
    # player disconnected before he sent his name
    if not user:
        return False
    players.append(client_socket)
    print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user))

    return True



while True:
    try:
        connection = SERVER_SOCKET.accept()
        new_connection(*connection)
    except KeyboardInterrupt:
        print('\nServer shutdown')
        SERVER_SOCKET.close()
        sys.exit()

    if len(players) == 2:
        for i in range(len(players)):
            players[i].send(str(i).encode('utf-8'))
        print('Game started!')