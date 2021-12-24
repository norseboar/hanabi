from .player import Player


def reorder_queue(queue, indexes_to_move_to_front):
    queue_front = []
    queue_back = []

    for i, c in enumerate(queue):
        if i in indexes_to_move_to_front:
            queue_front.append(c)
        else:
            queue_back.append(c)
    return queue_front + queue_back


class QueuePlayer(Player):
    """Abstract class for Queue Players, who keep a publicly-visible 'play queue' and
    'discard queue'"""

    def __init__(self, game, player_number):
        super().__init__(game, player_number)
        self.play_queue = []
        self.discard_queue = []

    def __repr__(self):
        s = super().__repr__()
        s += "  - Cards to play\n"
        for c in self.play_queue:
            s += "    - {}\n".format(c)
        s += "  - Cards to discard\n"
        for c in self.discard_queue:
            s += "    - {}\n".format(c)
        return s

    def get_hand(self):
        return self.play_queue + self.discard_queue

    def _add_card(self, card):
        self.discard_queue.append(card)

    def adjust_queues(self):
        """Adjust what should be played and discarded. Called each turn."""

        groups = self.group_cards()

        unknown_to_play = [c for c in groups["unknown"] if c in self.play_queue]
        unknown_to_discard = [c for c in groups["unknown"] if c in self.discard_queue]

        self.game.assert_(
            set(groups["unknown"]) == set(unknown_to_discard + unknown_to_play)
        )

        new_play_queue = unknown_to_play + groups["can_play_now"]
        new_discard_queue = (
            groups["unplayable"] + unknown_to_discard + groups["can_play_later"]
        )

        needed_numbers = self.game.get_needed_numbers()
        for c in new_play_queue:
            self.game.assert_(c.hinted_suit or c.hinted_number)
            if c.hinted_suit:
                self.game.assert_(c.suit in needed_numbers)

        self.play_queue = sorted(
            new_play_queue,
            key=lambda c: c.hinted_number
            if c.hinted_number
            else needed_numbers[c.hinted_suit],
        )
        self.discard_queue = new_discard_queue

    def group_cards(self):
        can_play_now = []
        can_play_later = []
        unplayable = []
        unknown = []

        needed_numbers = self.game.get_needed_numbers()

        for c in self.get_hand():
            if c.hinted_suit and c.hinted_number:
                if c.suit not in needed_numbers or c.number < needed_numbers[c.suit]:
                    unplayable.append(c)
                elif c.number == needed_numbers[c.suit]:
                    can_play_now.append(c)
                else:
                    self.game.assert_(c.number > needed_numbers[c.suit])
                    can_play_later.append(c)
            elif c.hinted_suit:
                if c.suit not in needed_numbers:
                    unplayable.append(c)
                else:
                    unknown.append(c)
            elif c.hinted_number:
                lowest_needed_number = min(needed_numbers.values())
                if c.number < lowest_needed_number:
                    unplayable.append(c)
                elif c.number not in needed_numbers.values():
                    can_play_later.append(c)
                else:
                    unknown.append(c)
            else:
                unknown.append(c)

        return {
            "can_play_now": can_play_now,
            "can_play_later": can_play_later,
            "unplayable": unplayable,
            "unknown": unknown,
        }

    def take_turn(self):
        super().take_turn()

        self.adjust_queues()
        self.take_action()

    def take_action(self):
        """Decide what action should be taken on a turn"""
        pass

    def receive_hint(self, hint):
        for c in self.play_queue:
            c.apply_hint(hint)

        target_card = None

        for c in self.discard_queue:
            hint_applies = c.apply_hint(hint)
            if not target_card and hint_applies:
                target_card = c

        self.act_on_target(target_card, hint)

    def act_on_target(self, target_card, _):
        self.move_to_play_queue(target_card)

    def move_to_play_queue(self, target_card):
        new_play_queue = self.play_queue.copy()
        new_discard_queue = self.discard_queue.copy()

        new_play_queue.append(target_card)
        new_discard_queue.remove(target_card)

        self.play_queue = new_play_queue
        self.discard_queue = new_discard_queue

    def play_from_hand(self):
        card = self.play_queue.pop(0)
        self.game.play_card(card)
        self.game.draw(self)

    def discard_from_hand(self):
        card = self.discard_queue.pop(0)
        self.game.discard_card(card)
        self.game.draw(self)
