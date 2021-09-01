import socket
import sys

from graphics import GGame

HEADER_LENGTH = 5
REQUESTS = {
    "buy_card": "0",
    "take_two_gems": "1",
    "take_three_gems": "2",
    "finish_turn": "3",
}


class ClientGame(GGame):
    def __init__(self, player_id: str, player_socket, init_state: str):
        super().__init__(player_id, init_state)
        self.p_socket = player_socket

    def get_response(self):
        while True:
            try:
                reply = receive_message(self.p_socket)
                break
            except IOError:
                continue
        if reply != 'False':
            self.state.update(reply)
            return True
        return False

    def request_buy_card(self, pos):
        send_message(self.p_socket, '{}{}{}'.format(REQUESTS['buy_card'], *pos))
        return self.get_response()

    def request_take_three_gems(self, gems: list):
        send_message(self.p_socket, '{}{}{}{}'.format(REQUESTS['take_three_gems'], *gems))
        return self.get_response()

    def request_take_two_gems(self, gem_id: int):
        send_message(self.p_socket, '{}{}'.format(REQUESTS['take_two_gems'], gem_id))
        return self.get_response()

    def request_finish_turn(self):
        send_message(self.p_socket, REQUESTS['finish_turn'])
        return self.get_response()

    def mouse_event_handler(self, event):
        if self.state.cur_player != self.state.id[0] or event.button != 1:
            return
        card = self.cardfield.get_clicked_card_coords(event.pos)
        gem = self.bank.get_clicked_bankgem_number(event.pos)
        button = self.get_clicked_button_id(event.pos)
        if not gem is False:
            self.clicked_gems.append(gem)
            if len(self.clicked_gems) == 3 and len(set(self.clicked_gems)) == 3:
                if self.request_take_three_gems(self.clicked_gems):
                    self.state.block = True
                self.clicked_gems.clear()
            if len(self.clicked_gems) == 2 and len(set(self.clicked_gems)) == 1:
                if self.request_take_two_gems(gem):
                    self.state.block = True
                self.clicked_gems.clear()
            if len(self.clicked_gems) >= 3:
                self.clicked_gems.clear()
        if card:
            if self.request_buy_card(card):
                self.state.block = True
            self.clicked_gems.clear()
        if button == 1:
            self.state.block = False
            self.request_finish_turn()
            self.clicked_gems.clear()

    def main(self):
        self.clicked_gems = []
        while not self.done:
            if self.state.cur_player != self.state.id[0]:
                try:
                    resp = receive_message(self.p_socket)
                    if resp != 'False':
                        self.state.update(resp)
                except IOError:
                    pass
            self.event_loop()
            self.draw()
        self.gameover()


def send_message(client_socket, message: str):
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)

def receive_message(client_socket):
    message_header = client_socket.recv(HEADER_LENGTH)
    if not message_header:
        print('Connection lost!')
        client_socket.close()
        sys.exit()
        return False
    message_length = int(message_header.decode('utf-8').strip())
    message = client_socket.recv(message_length).decode('utf-8')
    return message


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Please enter IP and port')
        sys.exit()

    IP = str(sys.argv[1])
    PORT = int(sys.argv[2])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    while True:
        username = input("Username: ").encode('utf-8')
        if len(username) < 16:
            break
        print("Username is too long! Try less than 16 symbols, please.")
    client_socket.send(username)

    while True:
        try:
            mes = receive_message(client_socket)
            if not mes:
                print('Connection closed by server')
                sys.exit()
            break
        except IOError:
            continue
    print('Game started')
    ClientGame(mes[0], client_socket, mes[1:]).main()
    client_socket.close()
