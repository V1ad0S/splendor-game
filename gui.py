import pygame as pg

COLORS = {
    "brown": [(128, 64, 0), (64, 32, 0),],
    "white": [(240, 240, 240), (210, 210, 210)],
    "red": [(210, 0, 0), (105, 0, 0)],
    "green": [(0, 210, 0), (0, 105, 0)],
    "blue": [(0, 0, 210), (0, 0, 105)]
}

def write_formated_letter(surface: 'pg.Surface', letter: str, coords: tuple):
    fonts = [[pg.font.Font(None, 111), (0, 0, 0)],
             [pg.font.Font(None, 85), (0, 0, 0)],
             [pg.font.Font(None, 100), (255, 255, 255)]]
    x, y = coords
    for font, i, j in zip(fonts, [x-2, x+3, x], [y-3, y+5, y]):
        surface.blit(font[0].render(str(letter), 1, font[1]), (i, j))


class GGemsInfo(pg.Surface):
    def __init__(self, assets: list, bonus: list):
        super(GGemsInfo, self).__init__((600, 100))
        self.info = []
        for i in range(5):
            gem = {"surf": pg.Surface((108, 90)),
                   "x_coord": 10 + 118 * i}
            self.info.append(gem)
        self.update(assets, bonus)

    def update(self, assets: list, bonus: list):
        for gem, asset, bon, color in zip(self.info, assets, bonus, COLORS.values()):
            gem['surf'].fill(color[1])
            surf = pg.Surface((49, 80))
            surf.fill(color[0])
            if bon:
                write_formated_letter(surf, str(bon), (6, 10))
            gem['surf'].blit(surf, (5, 5))
            if asset:
                write_formated_letter(gem['surf'], str(asset), (63, 15))
            self.blit(gem['surf'], (gem["x_coord"], 5))



class GCardField(pg.Surface):
    def __init__(self):
        super(GCardField, self).__init__((800, 420))


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
        self.size = (1280, 720)
        self.screen = pg.display.set_mode(self.size)
        self.done = False
        self.players_init()
        self.field_init()

    def players_init(self):
        self.player = GPlayer("Player_Name", [0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
        self.opponent = GPlayer("Opponent_Name", [0, 0, 0, 0, 0], [0, 0, 0, 0, 0])

    def field_init(self):
        self.cardfield = GCardField()
        self.bank = GBank([0, 0, 0, 0, 0], 5)

    def update_components(self):
        self.player.update([0, 1, 2, 3, 4], [5, 6, 7, 8, 9])
        self.opponent.update([5, 6, 7, 8, 9], [0, 1, 2, 3, 4])
        self.bank.update([0, 0, 0, 0, 0], 5)

    def draw(self):
        self.update_components()
        self.screen.fill((200, 200, 200))
        self.screen.blit(self.player, (50, 590))
        self.screen.blit(self.opponent, (50, 30))
        self.screen.blit(self.cardfield, (100, 150))
        self.screen.blit(self.bank, (930, 150))
        pg.display.update()

    def main(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                        self.done = True
            self.draw()

GGame().main()
