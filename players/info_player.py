from cards import Hint
from .player import Player


class InfoPlayer(Player):
    def __init__(self, game, player_number, weights):
        super().__init__(game, player_number, weights)
        self.hand = []

    def __repr__(self):
        s = super().__repr__()
        s += "  - Hand\n"
        for c in self.hand:
            s += "    - {}\n".format(c)
        return s

    def _add_card(self, card):
        self.hand.append(card)

    def get_hand(self):
        return self.hand

    def take_turn(self):
        moves = []
        for card in self.hand:
            moves.append(PlayMove(card))
            if self.game.hints < 8:
                moves.append(DiscardMove(card))
        if self.game.hints > 0:
            for p in self.game.players:
                hand = p.get_hand()
                for suit in self.game.suits:
                    if suit in [c.suit for c in hand]:
                        moves.append(HintMove(Hint(p, Hint.TYPE_SUIT, suit, self.game)))
                for number in range(1, self.game.MAX_NUMBER):
                    if number in [c.number for c in hand]:
                        moves.append(
                            HintMove(Hint(p, Hint.TYPE_NUMBER, number, self.game))
                        )

        best_score = -1
        best_move = None

        for m in moves:
            score = self.calculate_score(m)
            if score > best_score:
                best_move = m
                best_score = score

        self.execute(best_move)

    def calculate_score(self, move):
        if isinstance(move, PlayMove):
            possible_cards = []
            for card in self.game.get_remaining_card_list():
                if move.card.hinted_suit and move.card.hinted_number:
                    if (
                        move.card.hinted_suit == card.suit
                        and move.card.hinted_number == card.number
                    ):
                        possible_cards.append(card)
                elif move.card.hinted_suit:
                    if move.card.hinted_suit == card.suit:
                        possible_cards.append(card)
                elif move.card.hinted_number:
                    if move.card.hinted_number == card.number:
                        possible_cards.append(card)
                else:
                    possible_cards.append(card)

            playable_count = 0
            playable_five_count = 0
            for card in possible_cards:
                if self.game.is_card_playable(card):
                    playable_count += 1
                    if card.number == 5:
                        playable_five_count += 1
            avg_score_increase = round(playable_count / len(possible_cards), 4)
            avg_fail_increase = round(1 - avg_score_increase, 4)
            avg_hint_increase = round(playable_five_count / len(possible_cards), 4)

            return self.score_state(
                self.game.get_score() + avg_score_increase,
                self.get_knowledge_count(),
                self.game.hints + avg_hint_increase,
                self.game.fails + avg_fail_increase,
            )

        elif isinstance(move, HintMove):
            knowledge_increase = 0
            for c in move.hint.player.get_hand():
                if (
                    move.hint.type == Hint.TYPE_SUIT
                    and move.hint.value == c.suit
                    and (not c.hinted_suit)
                ):
                    knowledge_increase += 1
                if (
                    move.hint.type == Hint.TYPE_NUMBER
                    and move.hint.value == c.number
                    and (not c.hinted_number)
                ):
                    knowledge_increase += 1

            return self.score_state(
                self.game.get_score(),
                self.get_knowledge_count() + knowledge_increase,
                self.game.hints,
                self.game.fails,
            )
        elif isinstance(move, DiscardMove):
            return self.score_state(
                self.game.get_score(),
                self.get_knowledge_count(),
                self.game.hints + 1,
                self.game.fails,
            )
        else:
            self.game.assert_(False)

    def execute(self, move):
        if isinstance(move, PlayMove):
            self.hand.remove(move.card)
            self.game.play_card(move.card)
            self.game.draw(self)
        elif isinstance(move, HintMove):
            self.game.give_hint(move.hint)
        elif isinstance(move, DiscardMove):
            self.hand.remove(move.card)
            self.game.discard_card(move.card)
            self.game.draw(self)
        else:
            self.game.assert_(False)

    def get_knowledge_count(self):
        knowledge_count = 0
        for p in self.game.players:
            for c in p.get_hand():
                if c.hinted_suit:
                    knowledge_count += 1
                if c.hinted_number:
                    knowledge_count += 1
        return knowledge_count

    def score_state(self, game_score, knowledge_count, hints, fails):
        return (
            game_score * self.weights["GAME_SCORE"]
            + knowledge_count * self.weights["KNOWLEDGE_COUNT"]
            + hints * self.weights["HINTS"]
            + fails * self.weights["FAILS"]
        )


class Move:
    def __init__(self):
        pass


class PlayMove:
    def __init__(self, card):
        self.card = card

    def __repr__(self):
        return "Move: Play {}".format(self.card)


class HintMove:
    def __init__(self, hint):
        self.hint = hint

    def __repr__(self):
        return "Move: Hint {}".format(self.hint)


class DiscardMove:
    def __init__(self, card):
        self.card = card

    def __repr__(self):
        return "Move: Discard {}".format(self.card)
