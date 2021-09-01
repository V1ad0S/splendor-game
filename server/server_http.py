import json

from flask import Flask, request, jsonify

from baseclasses import Game
from services import make_dict_for_response, check_name


app = Flask(__name__)

players = []
current_player_id = 0
game = None
block = False

@app.route('/')
def index():
    return 'Splendor game server'

@app.route('/join', methods=['POST', 'GET'])
def new_connection():
    if request.method == 'GET':
        return jsonify(players)

    try:
        data = request.get_json()
        name = data['name']
    except KeyError:
        return make_dict_for_response('Json key "name" not found')
    except TypeError:
        return make_dict_for_response('Incorrect request. Json with "name" key was expected')


    if name_details := check_name(name, players):
        return make_dict_for_response(name_details)
    players.append(name)
    return make_dict_for_response()

@app.route('/disconnect/<string:name>')
def disconnect(name):
    global current_player_id, game, block
    current_player_id = 0
    game = None
    block = False
    players.remove(name)
    print(f'Player {name} disconnected')
    return make_dict_for_response('You are disconnected')

@app.route('/start_game/<string:name>')
def start_game(name):
    global game
    if len(players) == 2 and name in players:
        if not game:
            game = Game(players)
            game.lay_out_all()
        init_state = game.encode_state()
        return {'status': True, 'details': 'game starts', 'id': str(players.index(name)), 'init_state': init_state}
    if len(players) < 2:
        return make_dict_for_response('Waiting players')
    if name not in players:
        return make_dict_for_response("You aren't joined to the game")

@app.route('/game/<string:name>', methods=['POST', 'GET'])
def wait_move(name):
    global state, current_player_id, block
    if not game:
        return make_dict_for_response("Game isn't started")

    if request.method == 'GET':
        if current_player_id != players.index(name):
            return make_dict_for_response('Expect your turn')
        return {'status': True, 'details': 'Turn changed', 'state': game.encode_state()}

    try:
        data = request.get_json()
        name = data['name']
        move = data['move']
        details = data['details']
    except KeyError or TypeError:
        return make_dict_for_response('Incorrect request. Json with "name", "move", "details" keys was expected')
    if current_player_id != players.index(name):
        return make_dict_for_response('Expect your turn')
    move_dict = {
        "buy_card": game.buy_board_card,
        "take_two_gems": game.take_two_gems,
        "take_three_gems": game.take_three_gems,
    }
    if move == 'finish_turn':
        block = False
        current_player_id = (current_player_id + 1) % 2
        game.end_turn_checks()
        state = game.encode_state()
        return {'status': True, 'details': 'Successfully finish turn', 'state': state}
    # TODO: validate details
    result = None
    if move not in move_dict.keys():
        return make_dict_for_response(f'Incorrect move: {move}')
    if block:
        return make_dict_for_response('Denied')
    result = move_dict[move](details)
    if result:
        block = True
        return {'status': True, 'details': 'Correct move', 'state': game.encode_state()}
    return make_dict_for_response('Denied')


app.run()