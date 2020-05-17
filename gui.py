import pygame as pg

# добавить в GCard.update обработку None

COLORS = {
    "1": [(128, 64, 0), (64, 32, 0),],
    "2": [(240, 240, 240), (210, 210, 210)],
    "3": [(210, 0, 0), (105, 0, 0)],
    "4": [(0, 210, 0), (0, 105, 0)],
    "5": [(0, 0, 210), (0, 0, 105)]
}

def write_formated_letter(surface: 'pg.Surface', letter: str,
                          coords: tuple, color=(255, 255, 255)):
    fonts = [[pg.font.Font(None, 111), (0, 0, 0)],
             [pg.font.Font(None, 85), (0, 0, 0)],
             [pg.font.Font(None, 100), color]]
    x, y = coords
    for font, i, j in zip(fonts, [x-2, x+3, x], [y-3, y+5, y]):
        surface.blit(font[0].render(str(letter), 1, font[1]), (i, j))


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
                write_formated_letter(gem['surf_2'], str(bon), (6, 10))
            gem['surf_1'].blit(gem['surf_2'], (5, 5))
            if asset:
                write_formated_letter(gem['surf_1'], str(asset), (63, 15))
            self.blit(gem['surf_1'], (gem["x_coord"], 5))


class GCard(pg.Surface):
    def __init__(self, id: str):
        super(GCard, self).__init__((130, 180))
        self.update(id)

    def update(self, id):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        color = COLORS[id[0]][0]
        price_list = list(filter(lambda x: x[0] != '0', zip(id[2:], COLORS.values())))
        points = id[1]
        self.fill((10, 87, 87))
        write_formated_letter(self, points, (80, 0), color)
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
    def __init__(self, open_cards: list):
        super(GCardField, self).__init__((700, 550))
        self.open_cards = [[GCard(id) for id in row] for row in open_cards]

    def update(self, update_cards: list):
        j = 0
        for (row_1, row_2) in zip(self.open_cards, update_cards):
            i = 0
            for (card, card_id) in zip(row_1, row_2):
                card.update(card_id)
                self.blit(card, (135 * i, 185 * j))
                i += 1
            j += 1


class GPlayer(pg.Surface):
    def __init__(self, name: str, assets: list, bonus: list):
        super(GPlayer, self).__init__((1150, 100))
        self.name = pg.font.Font(None, 36).render(name, 1, (255, 255, 255))
        self.info = GGemsInfo(assets, bonus)

    def update(self, assets: list, bonus: list):
        self.blit(self.name, (10, 40))
        self.info.update(assets, bonus)
        self.blit(self.info, (220, 0))


class GBank(pg.Surface):
    def __init__(self, gems: list, gold: int):
        super(GBank, self).__init__((70, 420))
        self.gold = pg.Surface((70, 70))
        self.gems = []
        for i in range(5):
            gem = {"surf": pg.Surface((70, 70)),
                   "y_coord": 70 * (i+1)}
            self.gems.append(gem)
        self.update(gems, gold)

    def update(self, gems: list, gold: int):
        pg.draw.circle(self.gold, (255, 255, 0), (35, 35), 35)
        write_formated_letter(self.gold, str(gold), (16, 4))
        for gem, count, color in zip(self.gems, gems, COLORS.values()):
            pg.draw.circle(gem['surf'], color[0], (35, 35), 35)
            write_formated_letter(gem['surf'], count, (16, 4))
            self.blit(gem['surf'], (0, gem['y_coord']))
        self.blit(self.gold, (0, 0))


class GGame:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Splendor Game")
        pg.time.delay(100)
        self.size = (1280, 800)
        self.screen = pg.display.set_mode(self.size)
        self.done = False
        self.players_init()
        self.open_cards = [["1303353", "4335303", "5507003"],
                           ["1001111", "3031100", "5000131"],
                           ["2120230", "3132200", "4300060"]]
        self.field_init()

    def players_init(self):
        self.player = GPlayer("Player_Name", [0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
        self.opponent = GPlayer("Opponent_Name", [0, 0, 0, 0, 0], [0, 0, 0, 0, 0])

    def field_init(self):
        self.cardfield = GCardField(self.open_cards)
        self.bank = GBank([0, 0, 0, 0, 0], 5)

    def update_components(self):
        self.cardfield.update(self.open_cards)
        self.player.update([0, 1, 2, 3, 4], [5, 6, 7, 8, 9])
        self.opponent.update([5, 6, 7, 8, 9], [0, 1, 2, 3, 4])
        self.bank.update([0, 0, 0, 0, 0], 5)

    def draw(self):
        self.update_components()
        self.screen.fill((200, 200, 200))
        self.screen.blit(self.player, (50, 700))
        self.screen.blit(self.opponent, (50, 0))
        self.cardfield.update(self.open_cards)
        self.screen.blit(self.cardfield, (100, 120))
        self.screen.blit(self.bank, (1130, 150))
        pg.display.update()

    def main(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
            self.draw()

GGame().main()
