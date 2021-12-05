from datetime import datetime
from enum import Enum
import random
import sys

from numpy import mean, percentile, std
from tabulate import tabulate


LOG_PATH = "/Users/reed/hanabi/game_logs/"


class Suit(Enum):
    WHITE = "WHITE"
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    BLUE = "BLUE"
    RAINBOW = "RAINBOW"


class Card:
    def __init__(self, suit, number):
        self.suit = suit
        self.number = number
        self.hinted_suit = None
        self.hinted_number = None

    def __repr__(self):
        return "{} {}".format(self.suit, self.number)

    def __eq__(self, other):
        return self.suit == other.suit and self.number == other.number

    def match_hint(self, hint):
        if hint.type == Hint.TYPE_SUIT:
            return self.suit == hint.value
        elif hint.type == Hint.TYPE_NUMBER:
            return self.number == hint.value

    def apply_hint(self, hint):
        if hint.type == Hint.TYPE_SUIT and self.suit == hint.value:
            assert (self.hinted_suit is None) or (self.hinted_suit == hint.value)
            self.hinted_suit = hint.value
            return True

        if hint.type == Hint.TYPE_NUMBER and self.number == hint.value:
            assert (self.hinted_number is None) or (self.hinted_number == hint.value)
            self.hinted_number = hint.value
            return True

        return False


class Hint:
    TYPE_SUIT = "TYPE_SUIT"
    TYPE_NUMBER = "TYPE_NUMBER"

    def __init__(self, player, type, value):
        assert type == Hint.TYPE_SUIT or type == Hint.TYPE_NUMBER

        self.player = player
        self.type = type
        self.value = value


class Player:
    def __init__(self, game, player_number):
        self.game = game
        self.player_number = player_number

    def __repr__(self):
        s = "Player {}\n".format(self.player_number)
        return s

    def add_card(self, card):
        if not card:
            return
        self._add_card(card)

    def _add_card(self, card):
        pass

    def get_hand(self):
        pass

    def take_turn(self):
        pass

    def receive_hint(self, hint):
        pass


class FirstCardPlayer(Player):
    def __init__(self, game, player_number):
        Player.__init__(self, game, player_number)
        self.cards = []

    def __repr__(self):
        s = Player.__repr__(self)
        for c in self.cards:
            s += "  - {}\n".format(c)
        return s

    def get_hand(self):
        return self.cards

    def _add_card(self, card):
        self.cards.append(card)

    def take_turn(self):
        card = self.cards.pop(0)
        self.game.draw(self)
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
        s += "  - Cards to discard\n"
        for c in self.cards_to_discard:
            s += "    - {}\n".format(c)
        return s

    def get_hand(self):
        return self.cards_to_play + self.cards_to_discard

    def _add_card(self, card):
        self.cards_to_discard.append(card)

    def move_card_to_play(self, i):
        self.cards_to_play.insert(0, self.cards_to_discard.pop(i))

    def take_turn(self):
        # Adjust cards_to_play based on all information gotten from hits
        for i, card_to_discard in enumerate(self.cards_to_discard):
            for needed_card in self.game.get_needed_cards():
                if (
                    card_to_discard.hinted_suit == needed_card.suit
                    and card_to_discard.hinted_number == needed_card.number
                ):
                    self.move_card_to_play(i)

        # Make a play
        possible_hints = self.find_hints(self.game.players)

        if self.cards_to_play:
            self.play_from_hand()
        elif self.game.hints > 0 and possible_hints:
            self.game.give_hint(possible_hints[0])
        else:
            self.discard_from_hand()

    def find_hints(self, players):
        hints = []
        needed_cards = self.game.get_needed_cards()

        for p in players:
            if p == self:
                continue
            for card_to_discard in p.cards_to_discard:
                if card_to_discard not in needed_cards:
                    continue

                matching_suits = [
                    c for c in p.cards_to_discard if c.suit == card_to_discard.suit
                ]

                # We only want to give a hint if the first match should be played
                if card_to_discard == matching_suits[0]:
                    hints.append(Hint(p, Hint.TYPE_SUIT, card_to_discard.suit))

                matching_numbers = [
                    c for c in p.cards_to_discard if c.number == card_to_discard.number
                ]

                # We only want to give a hint if the first match should be played
                if card_to_discard == matching_numbers[0]:
                    hints.append(Hint(p, Hint.TYPE_NUMBER, card_to_discard.number))
        return hints

    def receive_hint(self, hint):
        matched_card = False
        for i, c in enumerate(self.cards_to_discard):
            hint_applies = c.apply_hint(hint)
            if not matched_card and hint_applies:
                matched_card = True
                self.move_card_to_play(i)

    def play_from_hand(self):
        card = self.cards_to_play.pop(0)
        self.game.draw(self)
        self.game.play_card(card)

    def discard_from_hand(self):
        card = self.cards_to_discard.pop(0)
        self.game.draw(self)
        self.game.discard_card(card)


class HelpfulDirectPlayer(DirectHintPlayer):
    def take_turn(self):
        # Adjust cards_to_play based on all information gotten from hits
        for i, card_to_discard in enumerate(self.cards_to_discard):
            for needed_card in self.game.get_needed_cards():
                if (
                    card_to_discard.hinted_suit == needed_card.suit
                    and card_to_discard.hinted_number == needed_card.number
                ):
                    self.move_card_to_play(i)

        # Make a play
        needy_players = [p for p in self.game.players if not p.cards_to_play]
        if self.game.hints > 0 and self.find_and_give_hint(needy_players):
            # find_and_give_hint already gives the hint, so there's nothing left to do
            pass
        elif self.cards_to_play:
            self.play_from_hand()
        elif self.game.hints > 0 and self.find_and_give_hint():
            # find_and_give_hint already gives the hint, so there's nothing left to do
            pass
        else:
            self.discard_from_hand()


class Game:
    def __init__(
        self,
        num_players,
        strategy,
        use_rainbow=False,
        should_print=True,
        log_file=None,
        seed=None,
    ):
        self.num_players = num_players
        self.strategy = strategy
        self.use_rainbow = use_rainbow
        self.should_print = should_print
        self.log_file = log_file

        if seed:
            self.seed = seed
        else:
            random.seed()
            self.seed = random.randint(0, sys.maxsize - 1)
        random.seed(self.seed)

        self.current_turn = 0
        self.turn_timer = num_players
        self.hints = 8
        self.fails = 0

        self.played_cards = {}
        for suit in self.get_suits():
            self.played_cards[suit] = []
        self.discarded_cards = []

        self.init_players(self.num_players, self.strategy)
        self.current_player = 0

        self.init_deck()

        for p in self.players:
            for i in range(5):
                p.add_card(self.deck.pop())

    def init_players(self, num_players, strategy):
        players = []
        for i in range(num_players):
            if strategy == "FIRST_CARD":
                players.append(FirstCardPlayer(self, i))
            elif strategy == "DIRECT_HINT":
                players.append(DirectHintPlayer(self, i))
            elif strategy == "HELPFUL_DIRECT":
                players.append(HelpfulDirectPlayer(self, i))
            else:
                assert False
        self.players = players

    def init_deck(self):
        deck = []
        for suit in self.get_suits():
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
        last_number = played_stack[-1].number if played_stack else 0

        if last_number == card.number - 1:
            played_stack.append(card)
            if card.number == 5:
                self.increment_hints

            self.log_string("Successfully played {}".format(card))
        else:
            self.fails += 1
            self.log_string("Failed to play {}".format(card))

    def discard_card(self, card):
        self.log_string("Discarded {}".format(card))
        self.discarded_cards.append(card)
        self.increment_hints()

    def give_hint(self, hint):
        self.log_string(
            "{} hint to player {}: {}".format(
                hint.type, hint.player.player_number, hint.value
            )
        )
        hint.player.receive_hint(hint)
        self.decrement_hints()

    def increment_hints(self):
        if self.hints < 8:
            self.hints += 1

    def decrement_hints(self):
        assert self.hints > 0
        self.hints -= 1

    def get_score(self):
        score = 0
        for s in self.get_suits():
            score += len(self.played_cards[s])
        return score

    def get_needed_cards(self):
        needed_cards = []
        for s in self.get_suits():
            last_number = self.played_cards[s][-1].number if self.played_cards[s] else 0
            if last_number == 5:
                break
            needed_cards.append(Card(s, last_number + 1))
        return needed_cards

    def get_suits(self):
        return [s for s in Suit if self.use_rainbow or s != Suit.RAINBOW]

    def run_turn(self, player, turn_number):
        self.log_string(
            """
==============================
            Turn {}
==============================
""".format(
                turn_number
            )
        )
        self.log_string(self.repr_global_state())
        player.take_turn()

    def run_game(self):
        self.log_string(
            """
============================================================
                        Starting game
                 Seed {} | {} Player | {} {}
============================================================
        """.format(
                self.seed,
                self.num_players,
                self.strategy,
                "with rainbow" if self.use_rainbow else "no rainbow",
            )
        )

        while self.fails < 3 and self.turn_timer >= 0:
            self.run_turn(self.players[self.current_player], self.current_turn)
            if not self.deck:
                self.turn_timer -= 1

            self.advance_player()
            self.current_turn += 1

        self.log_string(
            """
==============================
           Game Over
==============================
"""
        )
        self.log_string(self.repr_global_state())

        if self.fails >= 3:
            self.log_string("You hit three fails, you lose! Good day sir.")
        elif len(self.deck) <= 0:
            self.log_string("Out of cards")
        else:
            assert False

        return self.get_score()

    def repr_played_cards(self):
        repr = "Played cards:\n"
        for s in self.get_suits():
            repr += "  - {}: {}\n".format(str(s), len(self.played_cards[s]))
        return repr

    def repr_players(self):
        return "\n".join([str(p) for p in self.players])

    def repr_global_state(self):
        return """
Hints: {}
Fails: {}
Total score: {}
Current player: {}

{}

{}
        """.format(
            self.hints,
            self.fails,
            self.get_score(),
            self.current_player,
            self.repr_played_cards(),
            self.repr_players(),
        )

    def log_string(self, s):
        log_string(s, self.log_file, self.should_print)


def run_simulations(
    num_games,
    strategies,
    create_logs=False,
    use_rainbow=False,
    player_min=2,
    player_max=4,
):
    PERFECT_SCORE = (6 if use_rainbow else 5) * 5

    log_file_name = (
        LOG_PATH + "hanabi_log_" + datetime.now().isoformat(timespec="seconds") + ".txt"
    )

    log_file = None
    if create_logs:
        log_file = open(log_file_name, "w")

    for strategy in strategies:
        log_string(
            """
===========================================================================
Simulations for {} {}
===========================================================================
            """.format(
                strategy,
                "with rainbow" if use_rainbow else "no rainbow",
                log_file,
                should_print=True,
            ),
            log_file,
            should_print=True,
        )

        results = []
        for i in range(player_min, player_max + 1):
            scores = []
            for _ in range(num_games):
                g = Game(
                    i,
                    strategy,
                    use_rainbow,
                    should_print=False,
                    log_file=log_file,
                )
                scores.append(g.run_game())
            results.append(
                [
                    i,
                    round(mean(scores), 2),
                    percentile(scores, 10),
                    percentile(scores, 50),
                    percentile(scores, 90),
                    scores.count(PERFECT_SCORE),
                    round(std(scores), 2),
                ]
            )

        result_table = (
            tabulate(
                results,
                headers=["Players", "Mean", "P10", "P50", "P90", "Perfect", "std"],
                tablefmt="pretty",
            )
            + "\n"
        )
        log_string(result_table, log_file, should_print=True)

    if log_file:
        log_file.close()


def log_string(s, log_file, should_print):
    if log_file:
        log_file.write(s + "\n")
    if should_print:
        print(s)
