import random



class GemSet:
    """docstring for GemSet"""
    def __init__(self, gem_list: list):
        keys = ["brown", "white", "red", "green", "blue"]
        self.gems = {key : gem for (key, gem) in zip(keys, gem_list)}

    def __gt__(self, other: 'GemSet'):
        for key in self.gems.keys():
            if self.gems[key] < other.gems[key]:
                return False
        return True

    def __add__(self, other: 'GemSet'):
        result = []
        for key in self.gems.keys():
            result.append(self.gems[key] + other.gems[key])
        return GemSet(result)

    def __sub__(self, other: 'GemSet'):
        result = []
        for key in self.gems.keys():
            result.append(max(0, self.gems[key] - other.gems[key]))
        return GemSet(result)

    def __str__(self):
        return ' '.join([str(gem) for gem in self.gems.values()])

    def get_keys(self) -> 'dict_keys':
        return self.gems.keys()

    def get_gems(self, gem_key: str) -> int:
        return self.gems[gem_key]

    def add_gems(self, gem_key: str, amount: int):
        self.gems[gem_key] += max(0, amount)

    def remove_gems(self, gem_key: str, amount: int):
        self.gems[gem_key] = max(0, self.gems[gem_key] - amount)

    def get_count(self) -> int:
        return sum(self.gems.values())


class Bank:
    """docstring for Bank"""
    def __init__(self, players_number: int):
        self.gold = 5
        gems_per_color = 7
        if players_number == 2:
            gems_per_color = 4
        elif players_number == 3:
            gems_per_color = 5
        gems = [gems_per_color for _ in range(5)]
        self.gems = GemSet(gems)

    def __str__(self):
        return str(self.gems) + f"  Gold: {self.gold}"

    def add_gold(self, count):
        self.gold += count

    def dec_gold(self):
        if self.gold:
            self.gold = max(0, self.gold - 1)
            return True
        return False

    def add_gemset(self, gemset: 'GemSet'):
        self.gems += gemset

    def can_take_three_different(self, colors: list) -> bool:
        if len(set(colors)) != 3:
            return False
        for color in colors:
            if not self.gems.get_gems(color):
                return False
        return True

    def take_three_different(self, colors: list):
        for color in colors:
            self.gems.remove_gems(color, 1)
        gems_list = []
        for key in self.gems.get_keys():
            if key in colors:
                gems_list.append(1)
            else:
                gems_list.append(0)
        return GemSet(gems_list)

    def can_take_two_same(self, color: str) -> bool:
        if self.gems.get_gems(color) >= 4:
            return True
        return False

    def take_two_same(self, color: str) -> bool:
        self.gems.remove_gems(color, 2)
        gemset = GemSet([0, 0, 0, 0, 0])
        gemset.add_gems(color, 2)
        return gemset


class Card:
    """docstring for Card"""
    def __init__(self, card_id: str, color: str, points: int, price: list):
        self.id_string = card_id
        self.color = color
        self.points = points
        self.price = GemSet(price)

    def can_be_bought(self, assets: 'GemSet', bonus: 'GemSet', gold: int) -> bool:
        return (self.price - (assets + bonus)).get_count() <= gold

    def __str__(self):
        return f"Id: {self.id_string}, Price: {self.price}"

    def __repr__(self):
        return f"Card({self.id_string}, {self.price})"


class Noble:
    def __init__(self, noble_id: str, points: int, price: list):
        self.id_string = noble_id
        self.points = points
        self.price = GemSet(price)

    def will_visit(self, bonus):
        return bonus > self.price


class Deck:
    """Deck's class for game Splendor"""
    def __init__(self, class_of_card: 'Card or Noble', cards: dict):
        self.deck = [class_of_card(card_id, **card_values)
                     for (card_id, card_values) in cards.items()]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.deck)

    def pop(self) -> 'Card or Noble':
        if self.deck:
            return self.deck.pop()
        return None


class CardField:
    """CardField's class for game Splendor"""
    def __init__(self, decks: list):
        self.decks = [Deck(Card, deck) for deck in decks]
        self.cards_in_row = 4 # The number of cards in a row of open cards
        self.open_cards = [[] for i in range(len(decks))]

    def __str__(self):
        res = ''
        for row in self.open_cards:
            res += repr(row) + '\n'
        return res

    def lay_out(self):
        for (deck, cards_row) in zip(self.decks, self.open_cards):
            for _ in range(self.cards_in_row):
                cards_row.append(deck.pop())

    def pop_card(self, pos: tuple) -> 'Card':
        (row, col) = pos
        if (row < len(self.open_cards)) and (col < self.cards_in_row):
            card = self.open_cards[row][col]
            self.open_cards[row][col] = self.decks[row].pop()
            return card
        print(f"Index Error: {pos}")
        return None

    def get_card(self, pos: tuple) -> 'Card':
        (row, col) = pos
        if (row < len(self.open_cards)) and (col < self.cards_in_row):
            return self.open_cards[row][col]
        print(f"Index Error: {pos}")
        return None


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.nobles = []
        self.assets = GemSet([0, 0, 0, 0, 0])
        self.bonus = GemSet([0, 0, 0, 0, 0])
        self.gold = 0
        self.points = 0

    def add_gemset(self, gemset: 'GemSet'):
        self.assets += gemset

    def remove_gemset(self, gemset: 'GemSet'):
        self.assets -= gemset

    def inc_gold(self):
        self.gold += 1

    def remove_gold(self, amount: int):
        self.gold = max(0, self.gold - max(0, amount))

    def get_hand_size(self) -> int:
        return len(self.hand)

    def get_token_count(self) -> int:
        return self.assets.get_count() + self.gold

    def get_pay_info(self) -> list:
        return [self.assets, self.bonus, self.gold]

    def add_card(self, card: 'Card') -> list:
        """Returns gems and gold that must be returned to the bank"""
        gold_for_return = (card.price - self.bonus - self.assets).get_count()
        gems_for_return = ((card.price - self.bonus)
                           - (card.price - self.bonus - self.assets))
        self.remove_gold(gold_for_return)
        self.bonus.add_gems(card.color, 1)
        self.points += card.points
        self.remove_gemset(gems_for_return)
        return [gems_for_return, gold_for_return]

    def add_card_to_hand(self, card: 'Card'):
        self.hand.append(card)

    def get_card_from_hand(self, index: int):
        if 0 <= index <= len(self.hand):
            return self.hand[index]
        print(f"Index Error: {index}")
        return None

    def pop_card_from_hand(self, index: int) -> 'Card':
        if 0 <= index <= len(self.hand):
            card = self.hand[index]
            del self.hand[index]
            return card
        print(f"Index Error: {index}")
        return None


class Game:
    def __init__(self, decks: list, nobles: dict, players: list):
        self.players = players
        self.current_player = players[0]
        self.cardfield = CardField(decks)
        self.nobles = Deck(Noble, nobles)
        self.open_nobles = []
        self.bank = Bank(len(players))
        self.game_over = False

    def lay_out_all(self):
        self.cardfield.lay_out()
        for _ in range(len(self.players) + 1):
            self.open_nobles.append(self.nobles.pop())

    def take_three_gems(self, colors: list) -> bool:
        if self.bank.can_take_three_different(colors):
            self.current_player.add_gemset(self.bank.take_three_different(colors))
            return True
        print(f"Can't take 3 different gems: {colors}")
        return False

    def take_two_gems(self, color: str) -> bool:
        if self.bank.can_take_two_same(color):
            self.current_player.add_gemset(self.bank.take_two_same(color))
            return True
        print(f"Can't take 2 same gems: {color}")
        return False

    def buy_board_card(self, pos: tuple) -> bool:
        if card := self.cardfield.get_card(pos):
            if card.can_be_bought(*self.current_player.get_pay_info()):
                return_gems = self.current_player.add_card(card)
                self.cardfield.pop_card(pos)
                self.bank.add_gemset(return_gems[0])
                self.bank.add_gold(return_gems[1])
                return True
            print(f"Can't afford that card: {pos}.")
        else:
            print(f"Card[{pos}] doesn't exist.")
        return False

    def buy_hand_card(self, index: int) -> bool:
        if card := self.current_player.get_card_from_hand(index):
            if card.can_be_bought(*self.current_player.get_pay_info()):
                self.current_player.pop_card_from_hand(index)
                return_gems = self.current_player.add_card(card)
                self.bank.add_gemset(return_gems[0])
                self.bank.add_gold(return_gems[1])
                return True
            print(f"Can't afford that card: {index}.")
        else:
            print(f"Card[{index}] doesn't exist.")
        return False

    def reserve_card(self, pos: tuple) -> bool:
        if self.current_player.get_hand_size() >= 3:
            print("You have too many reservations.")
            return False
        if card := self.cardfield.pop_card(pos):
            self.current_player.add_card_to_hand(card)
            if self.bank.dec_gold():
                self.current_player.inc_gold()
            return True
        print(f"Card[{pos}] doesn't exist.")
        return False

    def end_turn_checks(self):
        """
        1. Checks if player has more than 10 tokens.
        2. Checks for noble visits.
        3. Shifts current to next player.
        4. If round is complete, checks if a player has won.
        """
