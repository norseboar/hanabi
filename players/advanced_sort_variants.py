from cards import Hint
from .advanced_queue_player import AdvancedQueuePlayer


class SortBasePlayer(AdvancedQueuePlayer):
    QUEUE_LENGTH_WEIGHT = 0
    PLAYER_POSITION_WEIGHT = 0
    CARD_NUMBER_WEIGHT = 0
    AFFECTED_CARD_WEIGHT = 0

    def score_hint(self, hint):
        score = 0
        score += (5 - len(hint.player.play_queue)) * self.QUEUE_LENGTH_WEIGHT

        relative_position = (
            hint.player.player_number - self.player_number
        ) % self.game.num_players
        score += (
            self.game.num_players - relative_position
        ) * self.PLAYER_POSITION_WEIGHT

        score += (5 - hint.target_card.number) * self.CARD_NUMBER_WEIGHT

        affected_card_count = 0
        for c in hint.player.discard_queue:
            if not c.match_hint(hint):
                continue
            if (hint.type == Hint.TYPE_SUIT and (not c.hinted_suit)) or (
                hint.type == Hint.TYPE_NUMBER and (not c.hinted_number)
            ):
                affected_card_count += 1
        score += affected_card_count * self.AFFECTED_CARD_WEIGHT

        return score

    def sort_hints(self, hints):
        return sorted(hints, key=self.score_hint, reverse=True)


class Sort1Player(SortBasePlayer):
    QUEUE_LENGTH_WEIGHT = pow(10, 4)
    AFFECTED_CARD_WEIGHT = pow(10, 3)
    PLAYER_POSITION_WEIGHT = pow(10, 1)
    CARD_NUMBER_WEIGHT = 0


class Sort2Player(SortBasePlayer):
    QUEUE_LENGTH_WEIGHT = pow(10, 3)
    AFFECTED_CARD_WEIGHT = pow(10, 4)
    PLAYER_POSITION_WEIGHT = pow(10, 1)
    CARD_NUMBER_WEIGHT = 0


class Sort3Player(SortBasePlayer):
    QUEUE_LENGTH_WEIGHT = pow(10, 3)
    AFFECTED_CARD_WEIGHT = 0
    PLAYER_POSITION_WEIGHT = pow(10, 1)
    CARD_NUMBER_WEIGHT = 0
