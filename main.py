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
        self.hinted_suit = None
        self.hinted_value = None

    def __repr__(self):
        return "{} {}".format(self.suit, self.value)

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value

    def set_hinted_suit(self, suit):
        assert (self.hinted_suit is None) or (self.hinted_suit == suit)
        self.hinted_suit = suit

    def set_hinted_value(self, value):
        assert (self.hinted_value is None) or (self.hinted_value == value)
        self.hinted_value = value


class Player:
    def __init__(self, game, player_number):
        self.game = game
        self.player_number = player_number

    def __repr__(self):
        s = "Player {}\n".format(self.player_number)
        return s

    def take_turn(self):
        pass


class RandomCardPlayer(Player):
    def __init__(self, game, player_number):
        Player.__init__(self, game, player_number)
        self.cards = []

    def __repr__(self):
        s = Player.__repr__(self)
        for c in self.cards:
            s += "  - {}\n".format(c)
        return s

    def add_card(self, card):
        if not card:
            return
        Player.add_card(self, card)
        self.cards.append(card)

    def take_turn(self):
        self.play_from_hand(0)

    def play_from_hand(self, card_index):
        card = self.cards.pop(card_index)
        self.game.draw(self)
        self.game.log_string("Player {} plays {}".format(self.player_number, card))
        self.game.play_card(card)


class DirectHintPlayer(Player):
    def __init__(self, game, player_number):
        Player.__init__(self, game, player_number)
        self.cards_to_play = []
        self.cards_to_discard = []

    def __repr__(self):
        s = Player.__repr__(self)
        s += "  - Cards to play\n"
        for c in self.cards_to_play:
            s += "    - {}\n".format(c)
        s += " - Cards to discard\n"
        for c in self.cards_to_discard:
            s += "    - {}\n".format(c)
        return s

    def add_card(self, card):
        if not card:
            return

        self.cards_to_discard.append(card)

    def move_card_to_play(self, i):
        self.cards_to_play.insert(0, self.cards_to_discard.pop(i))

    def take_turn(self):
        # Adjust cards_to_play based on all information gotten from hits
        for i, card_to_discard in enumerate(self.cards_to_discard):
            for needed_card in self.game.get_needed_cards():
                if (
                    card_to_discard.hinted_suit == needed_card.suit
                    and card_to_discard.hinted_value == needed_card.value
                ):
                    self.move_card_to_play(i)

        # Make a play
        if self.cards_to_play:
            self.play_from_hand()
        elif self.game.hints > 0 and self.find_and_give_hint():
            # find_and_give_hint already gives the hint, so there's nothing left to do
            pass
        else:
            self.discard_from_hand()

    def find_and_give_hint(self):
        needed_cards = self.game.get_needed_cards()
        for p in self.game.players:
            for card_to_discard in p.cards_to_discard:
                if card_to_discard in needed_cards:
                    # Numeric hints are generally better than suit hints, so we give that first
                    matching_values = [
                        c
                        for c in p.cards_to_discard
                        if c.value == card_to_discard.value
                    ]
                    # We only want to give a hint if the first match should be played
                    if card_to_discard == matching_values[0]:
                        p.take_value_hint(card_to_discard.value)
                        return True

                    matching_suits = [
                        c for c in p.cards_to_discard if c.suit == card_to_discard.suit
                    ]
                    if card_to_discard == matching_suits[0]:
                        p.take_suit_hint(card_to_discard.suit)
                        return True
        return False

    def evaluate_hint(player, needed_card, game):
        number_cards = [
            c for c in player.cards_to_discard if c.value == needed_card.value
        ]
        if number_cards and number_cards[0] == needed_card:
            pass

    def take_suit_hint(self, suit):
        matched_card = False
        for i, c in enumerate(self.cards_to_discard):
            if c.suit != suit:
                continue

            c.set_hinted_suit(suit)
            if not matched_card:
                matched_card = True
                self.move_card_to_play(i)

    def take_value_hint(self, value):
        matched_card = False
        for i, c in enumerate(self.cards_to_discard):
            if c.value != value:
                continue

            c.set_hinted_value(value)
            if not matched_card:
                matched_card = True
                self.move_card_to_play(i)

    def play_from_hand(self):
        card = self.cards_to_play.pop(0)
        self.game.draw(self)
        self.game.log_string("Player {} plays {}".format(self.player_number, card))
        self.game.play_card(card)

    def discard_from_hand(self):
        card = self.cards_to_discard.pop(0)
        self.game.draw(self)
        self.game.log_string("Player {} discards {}".format(self.player_number, card))
        self.game.discard_card(card)


class Game:
    def __init__(self, num_players, strategy, logging_enabled=True):
        self.logging_enabled = logging_enabled
        self.hints = 8
        self.fails = 0
        self.current_turn = 0
        self.turn_timer = num_players

        self.played_cards = {}
        for suit in Suit:
            self.played_cards[suit] = []
        self.discarded_cards = []

        self.num_players = num_players
        self.init_players(num_players, strategy)
        self.current_player = 0

        self.init_deck()

        for p in self.players:
            for i in range(5):
                p.add_card(self.deck.pop())

    def init_players(self, num_players, strategy):
        players = []
        for i in range(num_players):
            if strategy == "RANDOM_CARD":
                players.append(RandomCardPlayer(self, i))
            elif strategy == "DIRECT_HINT":
                players.append(DirectHintPlayer(self, i))
            else:
                assert False
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

    def draw(self, player):
        player.add_card(self.deck.pop() if self.deck else None)

    def play_card(self, card):
        played_stack = self.played_cards[card.suit]
        last_value = played_stack[-1].value if played_stack else 0

        if last_value == card.value - 1:
            played_stack.append(card)
            if card.value == 5:
                self.increment_hints

            self.log_string("Successfully played {}".format(card))
        else:
            self.fails += 1
            self.log_string("Failed to play {}".format(card))

    def discard_card(self, card):
        self.discarded_cards.append(card)
        self.increment_hints()

    def increment_hints(self):
        if self.hints < 8:
            self.hints += 1

    def decrement_hints(self):
        assert self.hints > 0
        self.hints -= 1

    def get_score(self):
        score = 0
        for s in Suit:
            score += len(self.played_cards[s])
        return score

    def get_needed_cards(self):
        needed_cards = []
        for s in Suit:
            last_value = self.played_cards[s][-1].value if self.played_cards[s] else 0
            if last_value == 5:
                break
            needed_cards.append(Card(s, last_value + 1))
        return needed_cards

    def run_turn(self, player):
        self.log_string(self.repr_global_state())
        player.take_turn()

    def run_game(self):
        while self.fails < 3 and self.turn_timer >= 0:
            self.run_turn(self.players[self.current_player])
            self.advance_player()
            self.current_turn += 1
            if not self.deck:
                self.turn_timer -= 1

        self.log_string(self.repr_global_state())

        score = self.get_score()
        if score == 5 * len(Suit):
            self.log_string("Perfect score!")
        elif self.fails >= 3:
            self.log_string("You hit three fails, you lose! Good day sir.")
        elif len(self.deck) <= 0:
            self.log_string("Out of cards")

        self.log_string("Game over")

        return score

    def repr_played_cards(self):
        repr = "Played cards:\n"
        for s in Suit:
            repr += "  - {}: {}\n".format(str(s), len(self.played_cards[s]))
        return repr

    def repr_global_state(self):
        return """
----- Turn {} Game State -----
Hints: {}
Fails: {}
Total score: {}
Current player: {}

{}


        """.format(
            self.current_turn,
            self.hints,
            self.fails,
            self.get_score(),
            self.current_player,
            self.repr_played_cards(),
        )

    def log_string(self, s):
        if self.logging_enabled:
            print(s)


def run_multiple(num_games, num_players, strategy):
    score_total = 0
    for i in range(num_games):
        g = Game(num_players, strategy, False)
        score_total += g.run_game()
    return score_total / num_games
