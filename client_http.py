import requests as req
import sys, time

from graphics import GGame


def make_move_dict_for_request(name: str, move: str, args) -> dict:
    return {'name': name, 'move': move, 'details': args}


class ClientGGame(GGame):
    def __init__(self, player_id: str, init_state: str, name: str, link: str = 'http://localhost:5000/'):
        super().__init__(player_id, init_state)
        self.name = name
        self.server_link = link

    def mouse_event_handler(self, event):
        if self.state.cur_player != self.state.id[0] or event.button != 1:
            return
        card = self.get_clicked_card_coords(event.pos)
        gem = self.get_clicked_bankgem_number(event.pos)
        button = self.get_clicked_button_id(event.pos)
        if gem >= 0:
            self.clicked_gems.append(gem)
            if len(self.clicked_gems) == 3 and len(set(self.clicked_gems)) == 3:
                if self.make_move_request('take_three_gems', self.clicked_gems):
                    self.state.block = True
                self.clicked_gems.clear()
            if len(self.clicked_gems) == 2 and len(set(self.clicked_gems)) == 1:
                if self.make_move_request('take_two_gems', gem):
                    self.state.block = True
                self.clicked_gems.clear()
            if len(self.clicked_gems) >= 3:
                self.clicked_gems.clear()
        if card:
            if self.make_move_request('buy_card', card):
                self.state.block = True
            self.clicked_gems.clear()
        if button == 1:
            self.state.block = False
            self.make_move_request('finish_turn', '')
            self.clicked_gems.clear()

    def main(self):
        self.clicked_gems = []
        while not self.done:
            if self.state.cur_player != self.state.id[0]:
                resp = req.get(f'{self.server_link}game/{self.name}')
                if resp.json()['status']:
                    self.state.update(resp.json()['state'])
                if resp.json()['details'] == "Game isn't started":
                    self.is_win = True
                    self.done = True
                time.sleep(1)
            self.event_loop()
            self.draw()
        self.gameover()

    def make_move_request(self, move: str, args):
        data = {
            'name': self.name,
            'move': move,
            'details': args,
        }
        resp = req.post(self.server_link + f'game/{self.name}', json=data)
        try:
            data = resp.json()
            status = data['status']
            details = data['details']
        except KeyError or TypeError:
            print('Incorrect server response')
            return False
        if status:
            state = data['state']
            self.state.update(state)
            return True
        if details == "Game isn't started":
            self.done = True
            self.is_win = True
        return False


if __name__ == '__main__':
    server = 'http://localhost:5000/'
    if len(sys.argv) == 2:
        server = str(sys.argv[1])
        if server[-1] != '/':
            server += '/'

    while True:
        try:
            name = input('Enter name:\t')
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            sys.exit(1)
        resp = req.post(server + 'join', json={'name': name})
        if resp.json()['status']:
            break
        print(resp.json()['details'])

    while True:
        resp = req.get(server + 'start_game/' + name)
        time.sleep(1)
        print(resp.json()['details'])
        if resp.json()['status']:
            id = resp.json()['id']
            init_state = resp.json()['init_state']
            break

    ClientGGame(id, init_state, name, server).main()
    req.get(server + 'disconnect/' + name)
