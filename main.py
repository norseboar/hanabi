from enum import Enum
import random


class Suit(Enum):
    WHITE = 0
    RED = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4
    RAINBOW = 5


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return "{} {}".format(self.suit, self.value)


class Player:
    def __init__(self, game, player_number):
        self.game = game
        self.player_number = player_number
        self.cards = []

    def __repr__(self):
        s = "Player {}\n".format(self.player_number)
        for c in self.cards:
            s += "  - {}\n".format(c)
        return s

    def take_turn(self):
        self.play_card_from_hand(0)

    def play_card_from_hand(self, card_index):
        card = self.cards.pop(card_index)
        self.cards.append(self.game.draw())
        print("Player {} plays {}".format(self.player_number, card))
        self.game.play_card(card)


class Game:
    def init_players(self, num_players):
        players = []
        for i in range(num_players):
            players.append(Player(self, i))
        self.players = players

    def init_deck(self):
        deck = []
        for suit in Suit:
            for i in range(3):
                deck.append(Card(suit, 1))
            for i in range(2):
                deck.append(Card(suit, 2))
                deck.append(Card(suit, 3))
                deck.append(Card(suit, 4))
            deck.append(Card(suit, 5))
        random.shuffle(deck)

        self.deck = deck

    def advance_player(self):
        next_player = self.current_player + 1
        self.current_player = next_player if next_player < self.num_players else 0

    def draw(self):
        return self.deck.pop()

    def play_card(self, card):
        played_stack = self.played_cards[card.suit]
        last_value = played_stack[-1].value if played_stack else 0

        if last_value == card.value - 1:
            played_stack.append(card)
            print("Successfully played {}".format(card))
        else:
            self.fails += 1
            print("Failed to play {}".format(card))

    def get_score(self):
        score = 0
        for s in Suit:
            score += len(self.played_cards[s])
        return score

    def run_turn(self, player):
        print(self.repr_global_state())
        player.take_turn()

    def run_game(self):
        while self.fails < 3 and len(self.deck) > 0:
            self.run_turn(self.players[self.current_player])
            self.advance_player()
            self.current_turn += 1

        print(self.repr_global_state())

        if self.get_score() == 5 * len(Suit):
            print("Perfect score!")
        elif self.fails >= 3:
            print("You hit three fails, you lose! Good day sir.")
        elif len(self.deck) <= 0:
            print("Out of cards")

        print("Game over")

    def repr_played_cards(self):
        repr = "Played cards:\n"
        for s in Suit:
            repr += "  - {}: {}\n".format(str(s), len(self.played_cards[s]))
        return repr

    def repr_global_state(self):
        return """
----- Turn {} Game State -----
Guesses: {}
Fails: {}
Total score: {}
Current player: {}

{}


        """.format(
            self.current_turn,
            self.guesses,
            self.fails,
            self.get_score(),
            self.current_player,
            self.repr_played_cards(),
        )

    def __init__(self, num_players):
        self.guesses = 8
        self.fails = 0
        self.current_turn = 0

        self.played_cards = {}
        for suit in Suit:
            self.played_cards[suit] = []

        self.num_players = num_players
        self.init_players(num_players)
        self.current_player = 0

        self.init_deck()

        for p in self.players:
            for i in range(5):
                p.cards.append(self.deck.pop())
