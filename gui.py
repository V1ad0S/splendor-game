import json
import pygame as pg
import socket
import sys

HEADER_LENGTH = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = {
    "1": [(128, 64, 0), (64, 32, 0),],
    "2": [(240, 240, 240), (210, 210, 210)],
    "3": [(210, 0, 0), (105, 0, 0)],
    "4": [(0, 210, 0), (0, 105, 0)],
    "5": [(0, 0, 210), (0, 0, 105)]
}

def write_formated_digit(surface: 'pg.Surface', digit: str,
                          coords: tuple, color=WHITE):
    fonts = [[pg.font.Font(None, 111), BLACK],
             [pg.font.Font(None, 85), BLACK],
             [pg.font.Font(None, 100), color]]
    x, y = coords
    for font, i, j in zip(fonts, [x-2, x+3, x], [y-3, y+5, y]):
        surface.blit(font[0].render(str(digit), 1, font[1]), (i, j))


class GGemsInfo(pg.Surface):
    def __init__(self, assets: list, bonus: list):
        super(GGemsInfo, self).__init__((600, 100))
        self.info = []
        for i in range(5):
            gem = {"surf_1": pg.Surface((108, 90)),
                   "surf_2": pg.Surface((49, 80)),
                   "x_coord": 10 + 118 * i}
            self.info.append(gem)
        self.update(assets, bonus)

    def update(self, assets: list, bonus: list):
        for gem, asset, bon, color in zip(self.info, assets, bonus, COLORS.values()):
            gem['surf_1'].fill(color[1])
            gem['surf_2'].fill(color[0])
            if bon:
                write_formated_digit(gem['surf_2'], str(bon), (6, 10))
            gem['surf_1'].blit(gem['surf_2'], (5, 5))
            if asset:
                write_formated_digit(gem['surf_1'], str(asset), (63, 15))
            self.blit(gem['surf_1'], (gem["x_coord"], 5))


class GCard(pg.Surface):
    def __init__(self, id: str):
        super(GCard, self).__init__((130, 180))
        self.update(id)

    def update(self, id: str):
        color = COLORS[id[0]][1]
        price_list = list(filter(lambda x: x[0] != '0', zip(id[2:], COLORS.values())))
        points = id[1]
        self.fill(color)
        write_formated_digit(self, points, (80, 0))
        i = 0
        for price in price_list:
            x, y = (23 + 41*(i % 3), 90 + 60*(i // 3))
            pg.draw.circle(self, price[1][0], (x, y), 18)
            p_1 = pg.font.Font(None, 47).render(price[0], 1, BLACK)
            p_2 = pg.font.Font(None, 57).render(price[0], 1, BLACK)
            p_3 = pg.font.Font(None, 50).render(price[0], 1, WHITE)
            self.blit(p_1, (x - 9, y - 14))
            self.blit(p_2, (x - 10, y - 17))
            self.blit(p_3, (x - 9, y - 15))
            i += 1


class GCardField(pg.Surface):
    def __init__(self, size: tuple, open_cards: list, decks_card_count: list):
        super(GCardField, self).__init__((size))
        self.open_cards = [[GCard(id) for id in row] for row in open_cards]
        self.decks = [pg.Surface((130, 180))] * 3
        self.update(open_cards, decks_card_count)

    def update(self, update_cards: list, decks_card_count: list):
        j = 0
        for (row_1, row_2) in zip(self.open_cards, update_cards):
            i = 0
            for (card, card_id) in zip(row_1, row_2):
                card.update(card_id)
                self.blit(card, (135 * i, 185 * j))
                i += 1
            j += 1
        i = 0
        decks_colors = [(51, 161, 34), (186, 189, 25), (27, 122, 181)]
        for (deck, count, col) in zip(self.decks, decks_card_count, decks_colors):
            deck.fill(col)
            g_count = pg.font.Font(None, 100).render(str(count), 1, WHITE)
            deck.blit(g_count, (25, 50))
            self.blit(deck, (570, 185 * i))
            i += 1


class GPlayer(pg.Surface):
    def __init__(self, name: str, assets: list, bonus: list):
        super(GPlayer, self).__init__((1150, 100))
        self.name = pg.font.Font(None, 36).render(name, 1, WHITE)
        self.info = GGemsInfo(assets, bonus)

    def update(self, assets: list, bonus: list, points: int):
        score = pg.font.Font(None, 40).render(f'Score: {points}', 1, WHITE)
        self.info.update(assets, bonus)
        self.blit(self.name, (10, 10))
        self.blit(score, (10, 50))
        self.blit(self.info, (220, 0))


class GBank(pg.Surface):
    def __init__(self, size: tuple, gems: list):
        super(GBank, self).__init__(size)
        self.gems = []
        for i in range(5):
            gem = {"surf": pg.Surface((size[0], size[0])),
                   "y_coord": size[0] * i}
            self.gems.append(gem)
        self.update(gems)

    def update(self, gems: list):
        rad = round(self.get_width() / 2)
        for gem, count, color in zip(self.gems, gems, COLORS.values()):
            pg.draw.circle(gem['surf'], color[0], (rad, rad), rad)
            write_formated_digit(gem['surf'], count, (16, 4))
            self.blit(gem['surf'], (0, gem['y_coord']))


class GButton(pg.Surface):
    def __init__(self, name: str):
        super(GButton, self).__init__((200, 100))
        self.name = pg.font.Font(None, 36).render(name, 1, WHITE)

    def update(self):
        self.fill(BLACK)
        self.blit(self.name, (10, 32))


class State:
    def __init__(self, player_id: str, state: dict):
        self.id = [player_id, str((int(player_id) + 1) % 2)]    # [player_id, opponent_id]
        self.update(state)

    def update(self, upd_state: dict):
        self.cur_player = upd_state['current_player']
        self.players = upd_state['players']
        self.cardfield = upd_state['cardfield']
        self.bank = upd_state['bank']


class GGame:
    def __init__(self, player_id: str, player_socket, init_state: str):
        pg.init()
        pg.display.set_caption("Splendor Game")
        pg.time.delay(100)
        self.size = (1280, 800)
        self.cardfield_coords = [(100, 120), (700, 550)]
        self.bank_coords = [(1130, 150), (70, 350)]
        self.screen = pg.display.set_mode(self.size)
        self.done = False
        self.p_socket = player_socket
        self.state_init(player_id, init_state)

    def state_init(self, player_id: str, init_state: str):
        state = json.loads(init_state)
        self.state = State(player_id, state)
        self.players_init()
        self.field_init()

    def players_init(self):
        player = self.state.players[self.state.id[0]]
        oppon = self.state.players[self.state.id[1]]
        self.player = GPlayer(player['name'], player['assets'], player['bonus'])
        self.opponent = GPlayer(oppon['name'], oppon['assets'], oppon['bonus'])

    def field_init(self):
        self.cardfield = GCardField(self.cardfield_coords[1],
                                    self.state.cardfield['open_cards'],
                                    self.state.cardfield['decks_card_count'])
        self.bank = GBank(self.bank_coords[1], self.state.bank['gems'])
        self.take_two_gems = GButton("Take 2 gems")
        self.take_three_gems = GButton("Take 3 gems")

    def update_state(self, state: str):
        upd_state = json.loads(state)
        self.state.update(upd_state)

    def update(self):
        player = self.state.players[self.state.id[0]]
        oppon = self.state.players[self.state.id[1]]
        self.player.update(player['assets'], player['bonus'], player['points'])
        self.opponent.update(oppon['assets'], oppon['bonus'], oppon['points'])
        self.cardfield.update(self.state.cardfield['open_cards'],
                              self.state.cardfield['decks_card_count'])
        self.bank.update(self.state.bank['gems'])
        self.take_two_gems.update()
        self.take_three_gems.update()

    def draw(self):
        self.update()
        self.screen.fill((200, 200, 200))
        self.screen.blit(self.player, (50, 700))
        self.screen.blit(self.opponent, (50, 0))
        self.screen.blit(self.cardfield, self.cardfield_coords[0])
        self.screen.blit(self.bank, self.bank_coords[0])
        self.screen.blit(self.take_two_gems, (850, 250))
        self.screen.blit(self.take_three_gems, (850, 400))
        pg.display.update()

    def check_button_click(self, pos):
        if pos[0] > 850 and pos[0] < 1050:
            if pos[1] > 250 and pos[1] < 350:
                return 1
            elif pos[1] > 400 and pos[1] < 500:
                return 2
        return False

    def check_card_click(self, pos):
        (x, y), (w, h) = self.cardfield_coords
        if pos[0] < x or pos[0] > (x + w - 165) or pos[1] < y or pos[1] > (y + h):
            return False
        click_pos = (pos[0] - x, pos[1] - y)
        card_coord = (click_pos[0] // 135, click_pos[1] // 185)
        return card_coord

    def check_bank_click(self, pos):
        (x, y), (w, h) = self.bank_coords
        if pos[0] < x or pos[0] > (x + w) or pos[1] < y or pos[1] > (y + h):
            return False
        num = (pos[1] - y) // w
        rad = round(w / 2)
        x_r, y_r = ((pos[0] - rad - x), ((pos[1] - y) % w - rad))
        if (x_r ** 2 + y_r ** 2) < rad ** 2:
            return num
        return False

    def main(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.state.cur_player == self.state.id[0] and event.button == 1:
                        print(self.check_card_click(event.pos))
                        print(self.check_bank_click(event.pos))
                        print(self.check_button_click(event.pos))
            self.draw()


def send_message(client_socket, message: str):
    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)

def recieve_message(client_socket):
    message_header = client_socket.recv(HEADER_LENGTH)
    if not message_header:
        return False
    message_length = int(message_header.decode('utf-8').strip())
    message = client_socket.recv(message_length).decode('utf-8')
    return message

if __name__ == '__main__':
    IP = 'localhost'
    PORT = 8000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    username = input("Username: ").encode('utf-8')
    client_socket.send(username)

    while True:
        try:
            mes = recieve_message(client_socket)
            if not mes:
                print('Connection closed by server')
                sys.exit()
            break
        except IOError:
            continue
    print('Game started')
    GGame(mes[0], client_socket, mes[1:]).main()
    client_socket.close()
