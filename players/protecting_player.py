from collections import defaultdict

from cards import Hint
from numpy.core.fromnumeric import sort

from click.decorators import group

from .advanced_sort_variants import SortBasePlayer


class ProtectingPlayer(SortBasePlayer):
    QUEUE_LENGTH_WEIGHT = pow(10, 5)
    PROTECT_PROXIMITY_0_WEIGHT = pow(10, 4)
    AFFECTED_CARD_WEIGHT = pow(10, 3)
    PLAYER_POSITION_WEIGHT = pow(10, 2)
    CARD_NUMBER_WEIGHT = 0
    PROTECT_PROXIMITY_1_WEIGHT = -1 * pow(10, 6)
    PROTECT_PROXIMITY_OTHER_WEIGHT = -1 * pow(10, 7)

    PURPOSE_ENDANGERED = "PURPOSE_ENDANGERED"

    def find_hints(self, players):
        hints = super().find_hints(players)
        needed_numbers = self.game.get_needed_numbers()
        endangered_cards = self.game.get_endangered_cards()

        for p in players:
            if p == self:
                continue

            for target_card in p.discard_queue:
                # Only send an endangered hint if the card is endangered, and the hint
                # cannot be mistaken for a hint to play the card
                if (
                    target_card.number not in endangered_cards[target_card.suit]
                    or target_card.number in needed_numbers.values()
                    or target_card.hinted_number
                ):
                    continue
                hints.append(
                    Hint(
                        p,
                        Hint.TYPE_NUMBER,
                        target_card.number,
                        self.game,
                        target_card,
                        purpose=self.PURPOSE_ENDANGERED,
                    )
                )

        return hints

    def score_hint(self, hint):
        score = super().score_hint(hint)
        card_proximity = hint.player.discard_queue.index(hint.target_card)

        if hint.purpose == self.PURPOSE_ENDANGERED:
            if card_proximity == 0:
                score += self.PROTECT_PROXIMITY_0_WEIGHT
            elif card_proximity == 1:
                score += self.PROTECT_PROXIMITY_1_WEIGHT
            else:
                score += self.PROTECT_PROXIMITY_OTHER_WEIGHT

        return score

    def act_on_target(self, target_card, hint):
        # If a number cannot be played, but is possibly playable later, assume it's
        # endangered and move it to the back of the discard queue
        needed_numbers = self.game.get_needed_numbers()
        if (
            hint.type == Hint.TYPE_NUMBER
            and hint.value not in needed_numbers.values()
            and hint.value > min(needed_numbers.values())
        ):
            new_discard_queue = [c for c in self.discard_queue if c != target_card]
            new_discard_queue.append(target_card)
            self.discard_queue = new_discard_queue
        else:
            super().act_on_target(target_card, hint)

    def take_action(self):
        sorted_hints = self.sort_hints(self.find_hints(self.game.players))
        top_hint = sorted_hints[0] if sorted_hints else None

        if (
            top_hint
            and self.game.hints > 0
            and top_hint.purpose == self.PURPOSE_ENDANGERED
            and top_hint.player.discard_queue[0] == top_hint.target_card
        ):
            self.game.give_hint(sorted_hints[0])
        elif self.play_queue:
            self.play_from_hand()
        elif self.game.hints > 0 and sorted_hints:
            self.game.give_hint(sorted_hints[0])
        else:
            self.discard_from_hand()

    def adjust_queues(self):
        super().adjust_queues()
        self.play_queue = list(reversed(self.play_queue))

    def group_cards(self):
        groups = super().group_cards()
        groups["can_play_later"] = sorted(
            groups["can_play_later"], key=lambda x: x.hinted_number or 0
        )
        return groups


class ProtectSort1Player(ProtectingPlayer):
    QUEUE_LENGTH_WEIGHT = pow(10, 5)
    PROTECT_PROXIMITY_0_WEIGHT = pow(10, 4)
    AFFECTED_CARD_WEIGHT = pow(10, 3)
    PLAYER_POSITION_WEIGHT = pow(10, 2)
    CARD_NUMBER_WEIGHT = 0
    PROTECT_PROXIMITY_1_WEIGHT = -1 * pow(10, 5)
    PROTECT_PROXIMITY_OTHER_WEIGHT = -1 * pow(10, 7)

    def take_action(self):
        sorted_hints = self.sort_hints(self.find_hints(self.game.players))

        if self.play_queue:
            self.play_from_hand()
        elif self.game.hints > 0 and sorted_hints:
            self.game.give_hint(sorted_hints[0])
        else:
            self.discard_from_hand()


class ProtectSort2Player(ProtectingPlayer):
    PROTECT_PROXIMITY_0_WEIGHT = -1 * pow(10, 10)
    QUEUE_LENGTH_WEIGHT = pow(10, 4)
    AFFECTED_CARD_WEIGHT = pow(10, 3)
    PLAYER_POSITION_WEIGHT = pow(10, 2)
    CARD_NUMBER_WEIGHT = 0
    PROTECT_PROXIMITY_1_WEIGHT = -1 * pow(10, 5)
    PROTECT_PROXIMITY_OTHER_WEIGHT = -1 * pow(10, 7)


class ProtectSort3Player(ProtectingPlayer):
    QUEUE_LENGTH_WEIGHT = pow(10, 5)
    PROTECT_PROXIMITY_0_WEIGHT = pow(10, 4)
    AFFECTED_CARD_WEIGHT = pow(10, 3)
    PLAYER_POSITION_WEIGHT = pow(10, 2)
    CARD_NUMBER_WEIGHT = 0
    PROTECT_PROXIMITY_1_WEIGHT = -1 * pow(10, 6)
    PROTECT_PROXIMITY_OTHER_WEIGHT = -1 * pow(10, 7)

    def take_action(self):
        sorted_hints = self.sort_hints(self.find_hints(self.game.players))
        top_hint = sorted_hints[0] if sorted_hints else None

        if (
            top_hint
            and self.game.hints > 0
            and top_hint.purpose == self.PURPOSE_ENDANGERED
            and top_hint.player.discard_queue[0] == top_hint.target_card
        ):
            self.game.give_hint(sorted_hints[0])
        elif self.play_queue:
            self.play_from_hand()
        elif self.game.hints > 0 and sorted_hints:
            self.game.give_hint(sorted_hints[0])
        else:
            self.discard_from_hand()


class ProtectSort4Player(ProtectingPlayer):
    QUEUE_LENGTH_WEIGHT = pow(10, 4)
    AFFECTED_CARD_WEIGHT = pow(10, 3)
    PLAYER_POSITION_WEIGHT = pow(10, 2)
    CARD_NUMBER_WEIGHT = 0
    PROTECT_PROXIMITY_0_WEIGHT = -1 * pow(10, 5)
    PROTECT_PROXIMITY_1_WEIGHT = -1 * pow(10, 6)
    PROTECT_PROXIMITY_OTHER_WEIGHT = -1 * pow(10, 7)


class BorderlineHintPlayer(ProtectingPlayer):
    PURPOSE_BORDERLINE_LIVE = "PURPOSE_BORDERLINE_LIVE"
    PURPOSE_BORDERLINE_DEAD = "PURPOSE_BORDERLINE_DEAD"

    QUEUE_LENGTH_WEIGHT = pow(10, 5)
    PROTECT_PROXIMITY_0_WEIGHT = pow(10, 4)
    AFFECTED_CARD_WEIGHT = pow(10, 3)
    PLAYER_POSITION_WEIGHT = pow(10, 2)
    CARD_NUMBER_WEIGHT = 0
    PROTECT_PROXIMITY_1_WEIGHT = -1 * pow(10, 6)
    BORDERLINE_DEAD_WEIGHT = -1 * pow(10, 7)
    PROTECT_PROXIMITY_OTHER_WEIGHT = -1 * pow(10, 8)
    BORDERLINE_LIVE_WEIGHT = -1 * pow(10, 9)

    def find_hints(self, players):
        hints = super().find_hints(players)

        needed_numbers = self.game.get_needed_numbers()
        needed_max = max(needed_numbers.values())
        needed_min = min(needed_numbers.values())
        dead_suits = [s for s in self.game.suits if s not in needed_numbers]

        for p in players:
            if p == self:
                continue
            for target_card in p.discard_queue:
                if target_card.number > needed_max and not target_card.hinted_number:
                    hints.append(
                        Hint(
                            p,
                            Hint.TYPE_NUMBER,
                            target_card.number,
                            self.game,
                            target_card,
                            purpose=self.PURPOSE_BORDERLINE_LIVE,
                        )
                    )
                if target_card.number < needed_min and not target_card.hinted_number:
                    hints.append(
                        Hint(
                            p,
                            Hint.TYPE_NUMBER,
                            target_card.number,
                            self.game,
                            target_card,
                            purpose=self.PURPOSE_BORDERLINE_DEAD,
                        )
                    )
                if target_card.suit in dead_suits and not target_card.hinted_suit:
                    hints.append(
                        Hint(
                            p,
                            Hint.TYPE_SUIT,
                            target_card.suit,
                            self.game,
                            target_card,
                            purpose=self.PURPOSE_BORDERLINE_DEAD,
                        )
                    )

        return hints

    def score_hint(self, hint):
        score = super().score_hint(hint)
        if hint.purpose == self.PURPOSE_BORDERLINE_LIVE:
            score += self.BORDERLINE_LIVE_WEIGHT
        if hint.purpose == self.PURPOSE_BORDERLINE_DEAD:
            score += self.BORDERLINE_DEAD_WEIGHT
        return score

    def take_action(self):
        sorted_hints = self.sort_hints(self.find_hints(self.game.players))
        top_hint = sorted_hints[0] if sorted_hints else None
        top_score = self.score_hint(top_hint) if top_hint else 0

        grouped_cards = self.group_cards()

        if (
            top_hint
            and self.game.hints > 0
            and top_hint.purpose == self.PURPOSE_ENDANGERED
            and top_hint.player.discard_queue[0] == top_hint.target_card
        ):
            self.game.give_hint(sorted_hints[0])
        elif self.play_queue:
            self.play_from_hand()
        elif (
            self.game.hints < 8
            and top_score < 0
            and self.discard_queue[0] in grouped_cards["unplayable"]
        ):
            self.discard_from_hand()
        elif self.game.hints < 8 and top_score < self.BORDERLINE_DEAD_WEIGHT:
            self.discard_from_hand()
        elif self.game.hints < 4 and top_score < 0:
            self.discard_from_hand()
        elif self.game.hints > 0 and sorted_hints:
            self.game.give_hint(sorted_hints[0])
        elif self.game.hints < 8:
            self.discard_from_hand()
        else:
            needed_numbers = self.game.get_needed_numbers()

            if grouped_cards["unknown"]:
                best_candidate = None
                best_matches = 0
                for c in grouped_cards["unknown"]:
                    num_matches = 0
                    if c.hinted_suit:
                        num_matches = 1
                    if c.hinted_number:
                        num_matches = list(needed_numbers.values()).count(
                            c.hinted_number
                        )
                    if num_matches > best_matches:
                        best_candidate = c
                        best_matches = num_matches
                self.move_to_play_queue(best_candidate or grouped_cards["unknown"][0])
            elif grouped_cards["unplayable"]:
                self.move_to_play_queue(grouped_cards["unplayable"][0])
            else:
                self.game.assert_(grouped_cards["can_play_later"])
                self.move_to_play_queue(grouped_cards["can_play_later"][0])

            self.play_from_hand()
