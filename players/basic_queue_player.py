from cards import Hint
from .queue_player import QueuePlayer


class BasicQueuePlayer(QueuePlayer):
    def take_action(self):
        hints = self.find_hints(self.game.players)

        if self.play_queue:
            self.play_from_hand()
        elif self.game.hints > 0 and hints:
            self.game.give_hint(self.sort_hints(hints)[0])
        else:
            self.discard_from_hand()

    def find_hints(self, players):
        hints = []

        needed_numbers = self.game.get_needed_numbers()

        for p in players:
            if p == self:
                continue

            for target_card in p.discard_queue:
                if needed_numbers.get(target_card.suit) != target_card.number:
                    continue

                matching_suits = [
                    c for c in p.discard_queue if c.suit == target_card.suit
                ]

                # We only want to give a hint if the first match should be played
                if target_card == matching_suits[0]:
                    hints.append(
                        Hint(
                            p,
                            Hint.TYPE_SUIT,
                            target_card.suit,
                            self.game,
                            target_card=target_card,
                        )
                    )

                matching_numbers = [
                    c for c in p.discard_queue if c.number == target_card.number
                ]

                # We only want to give a hint if the first match should be played
                if target_card == matching_numbers[0]:
                    hints.append(
                        Hint(
                            p,
                            Hint.TYPE_NUMBER,
                            target_card.number,
                            self.game,
                            target_card=target_card,
                        )
                    )
        return hints

    def sort_hints(self, hints):
        return hints
