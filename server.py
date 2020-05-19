import sys, socket, time
from baseclasses import Player, Game

IP = 'localhost'
PORT = 8000
HEADER_LENGTH = 5

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_SOCKET.bind((IP, PORT))
SERVER_SOCKET.listen()

players_sockets = []
players = []


print(f'Listening for connections on {IP}:{PORT}...')


def new_connection(client_socket, client_address):
    if len(players_sockets) >= 2:
        return False
    # player should send his name
    username = client_socket.recv(1024).decode('utf-8')
    # player disconnected before he sent his name
    if not username:
        return False
    players_sockets.append(client_socket)
    players.append(Player(username))
    print('Accepted new connection from {}:{}, username: {}'.format(*client_address, username))
    return True

def send_message(client_socket, message: str):
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)

def recieve_message(client_socket):
    message_header = client_socket.recv(HEADER_LENGTH)
    message_length = int(message_header.decode('utf-8').strip())
    message = client_socket.recv(message_length).decode('utf-8')
    return message


while True:
    try:
        connection = SERVER_SOCKET.accept()
        new_connection(*connection)
    except KeyboardInterrupt:
        print('\nServer shutdown')
        SERVER_SOCKET.close()
        sys.exit()

    if len(players_sockets) == 2:
        game = Game(players)
        game.lay_out_all()
        init_state = game.encode_state()
        for i in range(len(players_sockets)):
            send_message(players_sockets[i], str(i))
            send_message(players_sockets[i], init_state)
            time.sleep(2)
        print('Game started!')