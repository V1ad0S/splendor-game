import json, time
import pygame as pg

from graphics_settings import *


def load_images():
    files = ['card', 'circle', 'gem_bonus', 'gem_stats', 'panel_down', 'panel_up']
    images = dict()
    for fname in files:
        images[fname] = pg.image.load(f'images/{fname}.png')
    return images

def write_formated_digit(surface: 'pg.Surface', digit: str,
                          coords: tuple, color=WHITE):
    fonts = [[pg.font.Font(None, 111), BLACK],
             [pg.font.Font(None, 85), BLACK],
             [pg.font.Font(None, 100), color]]
    x, y = coords
    for font, i, j in zip(fonts, [x-2, x+3, x], [y-3, y+5, y]):
        surface.blit(font[0].render(str(digit), 1, font[1]), (i, j))


class GGemsInfo(pg.Surface):
    def __init__(self, asset, bonus, colors):
        super(GGemsInfo, self).__init__((160, 100), pg.SRCALPHA, 32)
        self.bonus_surf = pg.Surface((70, 90), pg.SRCALPHA, 32)
        self.image = images['gem_stats']
        self.bonus_image = images['gem_bonus']
        self.colors = colors
        self.update(asset, bonus)

    def update(self, asset, bonus):
        self.blit(self.image, (0, 0))
        self.fill(self.colors[1], special_flags=pg.BLEND_RGBA_MULT)
        if bonus:
            self.bonus_surf.blit(self.bonus_image, (0, 0))
            self.bonus_surf.fill(self.colors[0], special_flags=pg.BLEND_RGBA_MULT)
            write_formated_digit(self.bonus_surf, str(bonus), (15, 15))
            self.blit(self.bonus_surf, (8, 5))
        if asset:
            write_formated_digit(self, str(asset), (100, 20))


class GGemsInfoPanel(pg.Surface):
    def __init__(self, assets: list, bonuses: list, image):
        super(GGemsInfoPanel, self).__init__((960, 115), pg.SRCALPHA, 32)
        self.image = image
        self.info = [GGemsInfo(asset, bonus, col)
                     for asset, bonus, col in zip(assets, bonuses, COLORS.values())]
        self.update(assets, bonuses)
        self.blit(self.image, (0, 0))
        self.fill(GREEN, special_flags=pg.BLEND_RGBA_MULT)

    def update(self, assets: list, bonuses: list):
        for i, (gem_info, asset, bonus) in enumerate(zip(self.info, assets, bonuses)):
            gem_info.update(asset, bonus)
            self.blit(gem_info, (65 + 165 * i, 8))


class GCard(pg.Surface):
    def __init__(self, id: str):
        super(GCard, self).__init__((120, 170), pg.SRCALPHA, 32)
        self.images = [images['card'], images['circle']]
        self.update(id)

    def draw_circle(self, coords: tuple, color, value: int):
        circle = self.images[1].copy()
        circle.fill(color, special_flags=pg.BLEND_RGBA_MULT)
        p_1 = pg.font.Font(None, 47).render(value, 1, BLACK)
        p_2 = pg.font.Font(None, 57).render(value, 1, BLACK)
        p_3 = pg.font.Font(None, 50).render(value, 1, WHITE)
        circle.blit(p_1, (11, 6))
        circle.blit(p_2, (10, 3))
        circle.blit(p_3, (11, 5))
        self.blit(circle, coords)

    def update(self, id: str):
        if not id:
            self.fill(GREY, special_flags=pg.BLEND_RGBA_MULT)
            return
        color = COLORS[id[0]][1]
        price_list = list(filter(lambda x: x[0] != '0', zip(id[2:], COLORS.values())))
        points = id[1]
        self.blit(self.images[0], (0, 0))
        self.fill(color, special_flags=pg.BLEND_RGBA_MULT)
        write_formated_digit(self, points, (75, 0))
        i = 0
        for price in price_list:
            x, y = (5 + 45*(i % 2), 125 - 45*(i // 2))
            self.draw_circle((x, y), price[1][0], price[0])
            i += 1


class GCardField(pg.Surface):
    def __init__(self, size: tuple, open_cards: list, decks_card_count: list):
        super(GCardField, self).__init__(size)
        self.open_cards = [[GCard(id) for id in row] for row in open_cards]
        self.decks = [pg.Surface((120, 170), pg.SRCALPHA, 32) for _ in range(3)]
        self.update(open_cards, decks_card_count)

    def update(self, update_cards: list, decks_card_count: list):
        self.fill(BACKGROUND)
        for j, (row_1, row_2) in enumerate(zip(self.open_cards, update_cards)):
            for i, (card, card_id) in enumerate(zip(row_1, row_2)):
                card.update(card_id)
                self.blit(card, (125 * i, 175 * j))
        decks_colors = [(51, 161, 34), (186, 189, 25), (27, 122, 181)]
        for i, (deck, count, col) in enumerate(zip(self.decks, decks_card_count, decks_colors)):
            deck.blit(images['card'].copy(), (0, 0))
            deck.fill(col, special_flags=pg.BLEND_RGBA_MULT)
            g_count = pg.font.Font(None, 100).render(str(count), 1, WHITE)
            deck.blit(g_count, (22, 50))
            self.blit(deck, (570, 175 * i))

    def get_clicked_card_coords(self, pos):
        # pos: relative click coords
        (x, y), (w, h) = CARDFIELD_COORDS
        if pos[0] < x or pos[0] > (x + 120*4 + 5*3) or pos[1] < y or pos[1] > (y + h):
            return False
        click_pos = (pos[0] - x, pos[1] - y)
        card_coord = (click_pos[1] // 175, click_pos[0] // 125)
        return card_coord


class GPlayerBar(pg.Surface):
    def __init__(self, name: str, assets: list, bonus: list, image: 'loaded image'):
        super(GPlayerBar, self).__init__((1160, 115), pg.SRCALPHA, 32)
        self.name = pg.font.Font(None, 36).render(name, 1, WHITE)
        self.info = GGemsInfoPanel(assets, bonus, image)

    def update(self, assets: list, bonus: list, points: int):
        score = pg.font.Font(None, 40).render(f'Score: {points}', 1, WHITE)
        self.info.update(assets, bonus)
        self.fill(BACKGROUND)
        self.blit(self.name, (10, 10))
        self.blit(score, (10, 50))
        self.blit(self.info, (150, 0))


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
        self.fill(BACKGROUND)
        rad = round(self.get_width() / 2)
        for gem, count, color in zip(self.gems, gems, COLORS.values()):
            gem['surf'].fill(BACKGROUND)
            pg.draw.circle(gem['surf'], color[0], (rad, rad), rad)
            write_formated_digit(gem['surf'], count, (16, 4))
            self.blit(gem['surf'], (0, gem['y_coord']))

    def get_clicked_bankgem_number(self, pos):
        # pos - absolute click coords
        (x, y), (w, h) = BANK_COORDS
        if pos[0] < x or pos[0] > (x + w) or pos[1] < y or pos[1] > (y + h):
            return -1
        num = (pos[1] - y) // w
        rad = round(w / 2)
        x_r, y_r = ((pos[0] - rad - x), ((pos[1] - y) % w - rad))
        if (x_r ** 2 + y_r ** 2) < rad ** 2:
            return num
        return -1

class GButton(pg.Surface):
    def __init__(self, name: str, coords: tuple, size: tuple, button_id: int, font_size: int):
        super(GButton, self).__init__(size)
        self.font_size = font_size
        self.coords = coords
        self.size = size
        self.button_id = button_id
        self.name = pg.font.Font(None, self.font_size).render(name, 1, WHITE)

    def update(self, condition: int):
        if condition == 0:
            self.fill(GREY)
        elif condition == 1:
            self.fill(YELLOW)
        else:
            self.fill(GREEN)
        self.blit(self.name, (30, 25))

    def check_click(self, pos):
        if self.coords[0] < pos[0] < self.coords[0] + self.size[0]:
            if self.coords[1] < pos[1] < self.coords[1] + self.size[1]:
                return self.button_id
        return False


class State:
    def __init__(self, player_id: str, state: str):
        self.id = [player_id, str((int(player_id) + 1) % 2)]    # [player_id, opponent_id]
        self.block = False
        self.update(state)

    def update(self, upd_state: str):
        state = json.loads(upd_state)
        self.winner = state['winner']
        self.cur_player = state['current_player']
        self.players = state['players']
        self.cardfield = state['cardfield']
        self.bank = state['bank']


class GGame:
    def __init__(self, player_id: str, init_state: str):
        pg.init()
        pg.display.set_caption("Splendor Game")
        pg.time.delay(100)
        self.size = SCREEN_SIZE
        self.fps = FPS
        self.clock = pg.time.Clock()
        self.players_bars_coords = [(20, 0), (20, 685)]
        self.cardfield_coords = CARDFIELD_COORDS
        self.bank_coords = BANK_COORDS
        self.screen = pg.display.set_mode(self.size)
        self.done = False
        self.is_win = None
        self.state_init(player_id, init_state)

    def state_init(self, player_id: str, init_state: str):
        self.state = State(player_id, init_state)
        self.images = load_images()
        self.players_init()
        self.field_init()
        self.buttons_init()

    def players_init(self):
        player = self.state.players[self.state.id[0]]
        self.player = GPlayerBar(player['name'], player['assets'],
                              player['bonus'], images['panel_down'])
        oppon = self.state.players[self.state.id[1]]
        self.opponent = GPlayerBar(oppon['name'], oppon['assets'],
                                oppon['bonus'], images['panel_up'])

    def field_init(self):
        self.cardfield = GCardField(self.cardfield_coords[1],
                                    self.state.cardfield['open_cards'],
                                    self.state.cardfield['decks_card_count'])
        self.bank = GBank(self.bank_coords[1], self.state.bank['gems'])

    def buttons_init(self):
        self.buttons = {}
        self.buttons['complete_move'] = GButton("OK", (955, 550), (100, 70), 1, 36)

    def update(self):
        player = self.state.players[self.state.id[0]]
        oppon = self.state.players[self.state.id[1]]
        if self.state.winner:
            self.done = True
        self.player.update(player['assets'], player['bonus'], player['points'])
        self.opponent.update(oppon['assets'], oppon['bonus'], oppon['points'])
        self.cardfield.update(self.state.cardfield['open_cards'],
                              self.state.cardfield['decks_card_count'])
        self.bank.update(self.state.bank['gems'])
        btn_cond = int(self.state.id[0] == self.state.cur_player) + int(self.state.block)
        self.buttons['complete_move'].update(btn_cond)

    def draw(self):
        self.update()
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.player, self.players_bars_coords[1])
        self.screen.blit(self.opponent, self.players_bars_coords[0])
        self.screen.blit(self.cardfield, self.cardfield_coords[0])
        self.screen.blit(self.bank, self.bank_coords[0])
        for button in self.buttons.values():
            self.screen.blit(button, button.coords)
        pg.display.update()

    def get_clicked_button_id(self, pos):
        for button in self.buttons.values():
            clicked_button = button.check_click(pos)
            if clicked_button:
                return clicked_button
        return False

    def gameover(self):
        if self.is_win is None:
            self.is_win = self.state.winner == self.state.id[1]
        result = self.is_win * 'You won!' + (not self.is_win) * 'You lose!'
        res_surf = pg.font.Font(None, 150).render(result, 1, (200, 50, 50))
        self.screen.fill(BACKGROUND)
        self.screen.blit(res_surf, (400, 340))
        pg.display.update()
        time.sleep(1)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_event_handler(event)

    def mouse_event_handler(self, event):
        """This method is virtual"""
        pos = event.pos
        if (selected_gem := self.bank.get_clicked_bankgem_number(pos)) != -1:
            print(selected_gem)
        if selected_card := self.cardfield.get_clicked_card_coords(pos):
            print(selected_card)
        # print(event.pos)

    def main(self):
        """This method is virtual"""
        while not self.done:
            self.clock.tick(self.fps)
            self.event_loop()
            self.draw()
        self.gameover()

images = load_images()
if __name__ == '__main__':
    with open('init_state.json', 'r') as init_state_file:
        game = GGame("0", init_state_file.read())
    game.main()