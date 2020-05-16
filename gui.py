import pygame as pg


class GGemsInfo(pg.Surface):
    def __init__(self, assets: list, bonus: list):
        super(GGemsInfo, self).__init__((600, 100))
        self.colors = {
            "brown": (128, 64, 0),
            "white": (255, 255, 255),
            "red": (210, 0, 0),
            "green": (0, 210, 0),
            "blue": (0, 0, 210)
        }
        self.gems = []
        for i in range(5):
            gem = {"surf": pg.Surface((108, 90)),
                   "x_coord": 10 + 118 * i}
            self.gems.append(gem)
        self.update(assets, bonus)

    def update(self, assets: list, bonus: list):
        for gem, asset, bon, color in zip(self.gems, assets, bonus, self.colors.values()):
            gem['surf'].fill(color)
            self.blit(gem['surf'], (gem["x_coord"], 5))



class GCardField(pg.Surface):
    def __init__(self):
        super(GCardField, self).__init__((800, 420))


class GPlayer(pg.Surface):
    def __init__(self, name: str, assets: list, bonus: list):
        super(GPlayer, self).__init__((1150, 100))
        self.name = pg.font.Font(None, 36).render(name, 1, (255, 255, 255))
        self.gems = GGemsInfo(assets, bonus)

    def update(self):
        self.blit(self.name, (10, 40))
        self.gems.update([0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
        self.blit(self.gems, (220, 0))


class GBank(pg.Surface):
    def __init__(self):
        super(GBank, self).__init__((250, 380))


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Splendor Game")
        pg.time.delay(60)
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
        self.bank = GBank()

    def update_components(self):
        self.player.update()
        self.opponent.update()

    def draw(self):
        self.update_components()
        self.screen.fill((200, 200, 200))
        self.screen.blit(self.player, (50, 590))
        self.screen.blit(self.opponent, (50, 30))
        self.screen.blit(self.cardfield, (100, 150))
        self.screen.blit(self.bank, (930, 170))
        pg.display.update()

    def main(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                        self.done = True
            self.draw()

Game().main()
