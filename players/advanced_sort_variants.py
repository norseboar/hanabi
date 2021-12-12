from .advanced_queue_player import AdvancedQueuePlayer


class SortBasePlayer(AdvancedQueuePlayer):
    QUEUE_LENGTH_WEIGHT = 0
    PLAYER_POSITION_WEIGHT = 0
    CARD_NUMBER_WEIGHT = 0

    def sort_hints(self, hints):
        def score_hint(hint):
            score = 0
            score += (5 - len(hint.player.play_queue)) * self.QUEUE_LENGTH_WEIGHT

            relative_position = (
                hint.player.player_number - self.player_number
            ) % self.game.num_players
            score += (
                self.game.num_players - relative_position
            ) * self.PLAYER_POSITION_WEIGHT
            score += (5 - hint.target_card.number) * self.CARD_NUMBER_WEIGHT

            return score

        return sorted(hints, key=score_hint, reverse=True)


class Sort1Player(SortBasePlayer):
    QUEUE_LENGTH_WEIGHT = 1000
    PLAYER_POSITION_WEIGHT = 500
    CARD_NUMBER_WEIGHT = 0


class Sort2Player(SortBasePlayer):
    QUEUE_LENGTH_WEIGHT = 500
    PLAYER_POSITION_WEIGHT = 1000
    CARD_NUMBER_WEIGHT = 0


class Sort3Player(SortBasePlayer):
    QUEUE_LENGTH_WEIGHT = 0
    PLAYER_POSITION_WEIGHT = 0
    CARD_NUMBER_WEIGHT = -1000
