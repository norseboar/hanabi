from .basic_queue_player import BasicQueuePlayer


class AdvancedQueuePlayer(BasicQueuePlayer):
    def act_on_target(self, target_card, hint):
        needed_numbers = self.game.get_needed_numbers()
        if hint.type == hint.TYPE_SUIT:
            target_card.hinted_number = needed_numbers[hint.value]
        if (
            hint.type == hint.TYPE_NUMBER
            and list(needed_numbers.values()).count(hint.value) == 1
        ):
            for suit, number in needed_numbers.items():
                if number == hint.value:
                    target_card.hinted_suit = suit

        super().act_on_target(target_card, hint)
