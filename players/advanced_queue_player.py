from collections import defaultdict
from .basic_queue_player import BasicQueuePlayer


class AdvancedQueuePlayer(BasicQueuePlayer):
    # Whenever player gets a hint, it infers data about the other property
    def act_on_target(self, target_card, hint):
        needed_numbers = self.game.get_needed_numbers()
        if hint.type == hint.TYPE_SUIT and hint.value in needed_numbers:
            target_card.hinted_number = needed_numbers[hint.value]
            self.game.assert_(target_card.hinted_number == target_card.number)
        if (
            hint.type == hint.TYPE_NUMBER
            and hint.value in needed_numbers.values()
            and list(needed_numbers.values()).count(hint.value) == 1
        ):
            for suit, number in needed_numbers.items():
                if number == hint.value:
                    target_card.hinted_suit = suit
                    self.game.assert_(target_card.hinted_suit == target_card.suit)

        super().act_on_target(target_card, hint)

    def find_hints(self, players):
        hints = super().find_hints(players)

        pending_play = defaultdict(list)
        for p in self.game.players:
            if p == self:
                continue
            for c in p.play_queue:
                pending_play[c.suit].append(c.number)
        for c in self.play_queue:
            if c.hinted_suit and c.hinted_number:
                pending_play[c.hinted_suit].append(c.hinted_number)

        pruned_hints = []
        for h in hints:
            c = h.target_card
            if c and c.number not in pending_play[c.suit]:
                pruned_hints.append(h)

        return pruned_hints

    def receive_hint(self, hint):
        super().receive_hint(hint)
        self.adjust_queues()
