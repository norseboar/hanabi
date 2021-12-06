from datetime import datetime
from enum import Enum
import random
import sys

from numpy import mean, percentile, std
from tabulate import tabulate

from cards import Card, Suit
from players import (
    FirstCardPlayer,
    DirectHintPlayer,
    HelpfulDirectPlayer,
    SmartHints1Player,
    SmartHints2Player,
    SmartHints3Player,
    SmartHints4Player,
)

LOG_PATH = "/Users/reed/hanabi/game_logs/"


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

        self.played_cards = {}
        for suit in self.suits:
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
            elif strategy == "SMART_HINT_1":
                players.append(SmartHints1Player(self, i))
            elif strategy == "SMART_HINT_2":
                players.append(SmartHints2Player(self, i))
            elif strategy == "SMART_HINT_3":
                players.append(SmartHints3Player(self, i))
            elif strategy == "SMART_HINT_4":
                players.append(SmartHints4Player(self, i))
            else:
                assert False
        self.players = players

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
        played_stack = self.played_cards[card.suit]
        last_number = played_stack[-1].number if played_stack else 0
        return last_number == card.number - 1

    def play_card(self, card):
        played_stack = self.played_cards[card.suit]

        if self.is_card_playable(card):
            played_stack.append(card)
            if card.number == 5:
                self.increment_hints

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
            score += len(self.played_cards[s])
        return score

    def get_needed_cards(self):
        needed_cards = []
        for s in self.suits:
            last_number = self.played_cards[s][-1].number if self.played_cards[s] else 0
            if last_number == 5:
                break
            needed_cards.append(Card(s, last_number + 1))
        return needed_cards

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

        if self.should_log:  # Check this early b/c repr_global_state is expensive
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
        for s in self.suits:
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
            wasted_discard_pcts = []
            for _ in range(num_games):
                g = Game(
                    i,
                    strategy,
                    use_rainbow,
                    should_print=False,
                    log_file=log_file,
                )
                scores.append(g.run_game())
                wasted_discard_pcts.append(g.wasted_discards / g.current_turn)
            results.append(
                [
                    i,
                    round(mean(scores), 2),
                    percentile(scores, 10),
                    percentile(scores, 50),
                    percentile(scores, 90),
                    scores.count(PERFECT_SCORE),
                    round(std(scores), 2),
                    round(mean(wasted_discard_pcts) * 100, 2),
                ]
            )

        result_table = (
            tabulate(
                results,
                headers=[
                    "Players",
                    "Mean",
                    "P10",
                    "P50",
                    "P90",
                    "Perfect",
                    "std",
                    "Wasted discard %",
                ],
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
