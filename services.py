def make_dict_for_response(details: str = '') -> dict:
    return {'status': details == '', 'details': details}

def check_name(name: str, players: list):
    if len(players) < 2 and name not in players and name != '':
        return ''
    if name == '':
        return 'Empty string given'
    if len(players) >= 2:
        return 'Two players are already in the game'
    if name in players:
        return 'This name is already taken'