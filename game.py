import random
import sys

import click

from cards import Card, Suit
from players import STRATEGIES


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
        self.should_log = self.should_print or self.log_file
        self.suits = [s for s in Suit if self.use_rainbow or s != Suit.RAINBOW]

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
        self.wasted_discards = 0

        self.played_numbers = {}
        for suit in self.suits:
            self.played_numbers[suit] = 0
        self.discarded_cards = []

        self.init_players(self.num_players, self.strategy)
        self.current_player = 0

        self.init_deck()

        for p in self.players:
            for i in range(5):
                p.add_card(self.deck.pop())

    def init_players(self, num_players, strategy):
        self.players = []
        for i in range(num_players):
            assert strategy in STRATEGIES
            self.players.append(STRATEGIES[strategy](self, i))

    def init_deck(self):
        deck = []
        self.cards_remaining = {}
        for suit in self.suits:
            for i in range(3):
                deck.append(Card(suit, 1))
            for i in range(2):
                deck.append(Card(suit, 2))
                deck.append(Card(suit, 3))
                deck.append(Card(suit, 4))
            deck.append(Card(suit, 5))
            self.cards_remaining.update({suit: {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}})
        random.shuffle(deck)

        self.deck = deck

    def advance_player(self):
        next_player = self.current_player + 1
        self.current_player = next_player if next_player < self.num_players else 0

    def draw(self, player):
        player.add_card(self.deck.pop() if self.deck else None)

    def is_card_playable(self, card):
        return self.played_numbers[card.suit] == card.number - 1

    def play_card(self, card):
        if self.is_card_playable(card):
            self.played_numbers[card.suit] += 1
            if card.number == 5:
                self.increment_hints()
            self.log_string("Successfully played {}".format(card))
        else:
            self.fails += 1
            self.log_string("Failed to play {}".format(card))

    def discard_card(self, card):
        self.log_string("Discarded {}".format(card))
        if self.hints == 8:
            self.wasted_discards += 1
        self.discarded_cards.append(card)
        self.increment_hints()
        self.cards_remaining[card.suit][card.number] -= 1

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
        for s in self.suits:
            score += self.played_numbers[s]
        return score

    def get_needed_numbers(self):
        needed_numbers = {}
        for s in self.suits:
            if self.played_numbers[s] == 5:
                continue
            needed_numbers[s] = self.played_numbers[s] + 1
        return needed_numbers

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
        if self.should_log:  # Check this early b/c repr_global_state is expensive
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

        while (
            self.fails < 3
            and self.turn_timer >= 0
            and sum(self.played_numbers.values()) < 5 * len(self.suits)
        ):
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

        if self.should_log:  # Check this early b/c repr_global_state is expensive
            self.log_string(self.repr_global_state())

        if self.fails >= 3:
            self.log_string("You hit three fails, you lose! Good day sir.")
        elif len(self.deck) <= 0:
            self.log_string("Out of cards")
        elif sum(self.played_numbers.values()) >= 5 * len(self.suits):
            self.log_string("You got a perfect score!!")
        else:
            assert False

        return self.get_score()

    def repr_played_cards(self):
        repr = "Played cards:\n"
        for s in self.suits:
            repr += "  - {}: {}\n".format(str(s), self.played_numbers[s])
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


def log_string(s, log_file, should_print):
    if log_file:
        log_file.write(s + "\n")
    if should_print:
        click.echo(s)
