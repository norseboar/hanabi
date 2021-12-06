from cards import Hint


def reorder_queue(queue, indexes_to_move_to_front):
    queue_front = []
    queue_back = []

    for i, c in enumerate(queue):
        if i in indexes_to_move_to_front:
            queue_front.append(c)
        else:
            queue_back.append(c)
    return queue_front + queue_back


class Player:
    def __init__(self, game, player_number):
        self.game = game
        self.player_number = player_number

    def __repr__(self):
        s = "Player {}\n".format(self.player_number)
        return s

    def add_card(self, card):
        if not card:
            return
        self._add_card(card)

    def _add_card(self, card):
        pass

    def get_hand(self):
        pass

    def take_turn(self):
        self.adjust_cards()

    def adjust_cards(self):
        pass

    def receive_hint(self, hint):
        pass


class FirstCardPlayer(Player):
    def __init__(self, game, player_number):
        super().__init__(game, player_number)
        self.cards = []

    def __repr__(self):
        s = Player.__repr__(self)
        for c in self.cards:
            s += "  - {}\n".format(c)
        return s

    def get_hand(self):
        return self.cards

    def _add_card(self, card):
        self.cards.append(card)

    def take_turn(self):
        super().take_turn()
        card = self.cards.pop(0)
        self.game.draw(self)
        self.game.play_card(card)


class DirectHintPlayer(Player):
    DISCARD_TO_PLAY = "DISCARD_TO_PLAY"
    PLAY_TO_DISCARD = "PLAY_TO_DISCARD"
    CARD_DEAD = "CARD_DEAD"
    CARD_UNPLAYABLE = "CARD_UNPLAYABLE"
    CARD_POTENTIALLY_PLAYABLE = "CARD_PLAYABLE"

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

    def move_cards_between_queues(self, front_indexes, back_indexes, move_type):
        assert move_type in [self.DISCARD_TO_PLAY, self.PLAY_TO_DISCARD]

        # Create a new immutable list to avoid index iteration issues
        new_src_queue = []

        src_queue = None
        dest_queue = None
        if move_type == self.DISCARD_TO_PLAY:
            src_queue = self.discard_queue
            dest_queue = self.play_queue
        elif move_type == self.PLAY_TO_DISCARD:
            src_queue = self.play_queue
            dest_queue = self.discard_queue

        for i, _ in enumerate(src_queue):
            if i in front_indexes:
                dest_queue.insert(0, src_queue[i])
            elif i in back_indexes:
                dest_queue.append(src_queue[i])
            else:
                new_src_queue.append(src_queue[i])

        if move_type == self.DISCARD_TO_PLAY:
            self.discard_queue = new_src_queue
        elif move_type == self.PLAY_TO_DISCARD:
            self.play_queue = new_src_queue

    def sort_hints(self, hints):
        return hints

    def take_turn(self):
        super().take_turn()

        possible_hints = self.sort_hints(self.find_hints(self.game.players))

        if self.play_queue:
            self.play_from_hand()
        elif self.game.hints > 0 and possible_hints:
            self.game.give_hint(possible_hints[0])
        else:
            self.discard_from_hand()

    def adjust_cards(self):
        # Move any cards we know can be played to the play queue
        playable_card_indexes = []
        needed_cards = self.game.get_needed_cards()

        all_play_queue = []
        for p in self.game.players:
            all_play_queue += p.play_queue

        for i, card_to_discard in enumerate(self.discard_queue):
            if not (card_to_discard.hinted_suit and card_to_discard.hinted_number):
                continue

            for needed_card in needed_cards:
                if (
                    card_to_discard.hinted_suit == needed_card.suit
                    and card_to_discard.hinted_number == needed_card.number
                    and card_to_discard not in all_play_queue
                ):
                    playable_card_indexes.append(i)
        self.move_cards_between_queues(playable_card_indexes, [], self.DISCARD_TO_PLAY)

        # Move any cards we know we cannot play to the discard queue
        dead_card_indexes = []
        play_later_indexes = []
        for i, card_to_play in enumerate(self.play_queue):
            card_status = self.get_card_status(card_to_play)
            if card_status == self.CARD_DEAD:
                dead_card_indexes.append(i)
            elif card_status == self.CARD_UNPLAYABLE:
                play_later_indexes.append(i)
            else:
                assert card_status == self.CARD_POTENTIALLY_PLAYABLE
        self.move_cards_between_queues(
            dead_card_indexes, play_later_indexes, self.PLAY_TO_DISCARD
        )

        # Move any cards we know are bad to the front of the discard
        dead_card_indexes = []
        for i, card_to_discard in enumerate(self.discard_queue):
            if self.get_card_status(card_to_discard) == self.CARD_DEAD:
                dead_card_indexes.append(i)
        self.discard_queue = reorder_queue(self.discard_queue, dead_card_indexes)

    def get_card_status(self, card):
        played_stack = self.game.played_cards[card.suit]
        last_number = played_stack[-1].number if played_stack else 0

        if card.hinted_suit and card.hinted_number:
            if card.number <= last_number:
                return self.CARD_DEAD
            elif card.number > last_number + 1:
                return self.CARD_UNPLAYABLE
        elif card.hinted_suit:
            if last_number == 5:
                return self.CARD_DEAD
        elif card.hinted_number:
            lowest_playable_number = 6
            for suit in self.game.suits:
                played_stack = self.game.played_cards[suit]
                last_number = played_stack[-1].number if played_stack else 0
                if last_number + 1 < lowest_playable_number:
                    lowest_playable_number = last_number + 1
            if card.number < lowest_playable_number:
                return self.CARD_DEAD
        return self.CARD_POTENTIALLY_PLAYABLE

    def find_hints(self, players):
        hints = []
        needed_cards = self.game.get_needed_cards()

        all_play_queue = []
        for p in players:
            all_play_queue += p.play_queue

        for p in players:
            if p == self:
                continue
            for card_to_discard in p.discard_queue:
                if (
                    card_to_discard in all_play_queue
                    or card_to_discard not in needed_cards
                ):
                    continue

                matching_suits = [
                    c for c in p.discard_queue if c.suit == card_to_discard.suit
                ]

                # We only want to give a hint if the first match should be played
                if card_to_discard == matching_suits[0]:
                    hints.append(
                        Hint(p, Hint.TYPE_SUIT, card_to_discard.suit, card_to_discard)
                    )

                matching_numbers = [
                    c for c in p.discard_queue if c.number == card_to_discard.number
                ]

                # We only want to give a hint if the first match should be played
                if card_to_discard == matching_numbers[0]:
                    hints.append(
                        Hint(
                            p, Hint.TYPE_NUMBER, card_to_discard.number, card_to_discard
                        )
                    )
        return hints

    def receive_hint(self, hint):
        matched_card = False
        for i, c in enumerate(self.discard_queue):
            hint_applies = c.apply_hint(hint)
            if not matched_card and hint_applies:
                matched_card = True
                self.move_cards_between_queues([i], [], self.DISCARD_TO_PLAY)

    def play_from_hand(self):
        card = self.play_queue.pop(0)
        self.game.draw(self)
        self.game.play_card(card)

    def discard_from_hand(self):
        card = self.discard_queue.pop(0)
        self.game.draw(self)
        self.game.discard_card(card)


class HelpfulDirectPlayer(DirectHintPlayer):
    def take_turn(self):
        Player.take_turn(self)

        needy_players = [p for p in self.game.players if not p.play_queue]
        needy_hints = self.find_hints(needy_players)
        all_hints = self.find_hints(self.game.players)

        if self.game.hints > 0 and needy_hints:
            self.game.give_hint(needy_hints[0])
        elif self.play_queue:
            self.play_from_hand()
        elif self.game.hints > 0 and all_hints:
            self.game.give_hint(all_hints[0])
        else:
            self.discard_from_hand()


class SmartHints1Player(DirectHintPlayer):
    def sort_hints(self, hints):
        def score_hint(hint):
            score = 0
            score += (5 - len(hint.player.play_queue)) * 100

            relative_position = (
                hint.player.player_number - self.player_number
            ) % self.game.num_players
            score += (self.game.num_players - relative_position) * 1000

            return score

        return sorted(hints, key=score_hint, reverse=True)


class SmartHints2Player(DirectHintPlayer):
    def sort_hints(self, hints):
        def score_hint(hint):
            score = 0
            score += (5 - len(hint.player.play_queue)) * 1000

            relative_position = (
                hint.player.player_number - self.player_number
            ) % self.game.num_players
            score += (self.game.num_players - relative_position) * 100

            return score

        return sorted(hints, key=score_hint, reverse=True)


class SmartHints3Player(DirectHintPlayer):
    def sort_hints(self, hints):
        def score_hint(hint):
            score = 0
            score += (5 - len(hint.player.play_queue)) * 1000

            relative_position = (
                hint.player.player_number - self.player_number
            ) % self.game.num_players
            score += (self.game.num_players - relative_position) * 100

            score += (5 - hint.target_card.number) * 10000

            return score

        return sorted(hints, key=score_hint, reverse=True)


class SmartHints4Player(DirectHintPlayer):
    def sort_hints(self, hints):
        def score_hint(hint):
            score = 0
            score += (5 - len(hint.player.play_queue)) * 100

            relative_position = (
                hint.player.player_number - self.player_number
            ) % self.game.num_players
            score += (self.game.num_players - relative_position) * 1000

            score += (5 - hint.target_card.number) * 10000

            return score

        return sorted(hints, key=score_hint, reverse=True)


class ProtectCardsPlayer(SmartHints3Player):
    def find_hints(self, players):
        hints = []
        needed_cards = self.game.get_needed_cards()

        all_play_queue = []
        for p in players:
            all_play_queue += p.play_queue

        for p in players:
            if p == self:
                continue
            for card_to_discard in p.discard_queue:
                if card_to_discard in all_play_queue:
                    continue
                
                # First create hints for cards that should be played
                if card_to_discard in needed_cards:
                    matching_suits = [
                        c for c in p.discard_queue if c.suit == card_to_discard.suit
                    ]

                    # We only want to give a hint if the first match should be played
                    if card_to_discard == matching_suits[0]:
                        hints.append(
                            Hint(
                                p,
                                Hint.TYPE_SUIT,
                                card_to_discard.suit,
                                card_to_discard,
                                purpose=Hint.PURPOSE_PLAY,
                            )
                        )

                    matching_numbers = [
                        c for c in p.discard_queue if c.number == card_to_discard.number
                    ]

                    # We only want to give a hint if the first match should be played
                    if card_to_discard == matching_numbers[0]:
                        hints.append(
                            Hint(
                                p,
                                Hint.TYPE_NUMBER,
                                card_to_discard.number,
                                card_to_discard,
                                purpose=Hint.PURPOSE_PLAY,
                            )
                        )
                elif self.game.cards_remaining[card_to_discard.suit][card_to_discard.value] <= 1:
                    assert self.game.cards_remaining[card_to_discard.suit][card_to_discard.value] == 1
                    matching_suits = [
                        c for c in p.discard_queue if c.suit == card_to_discard.suit
                    ]

                    # We only want to give a hint if nothing can be played
                    
                    ####### NEEDS WORK ######


                    # if card_to_discard == matching_suits[0]:
                    #     hints.append(
                    #         Hint(
                    #             p,
                    #             Hint.TYPE_SUIT,
                    #             card_to_discard.suit,
                    #             card_to_discard,
                    #             purpose=Hint.PURPOSE_PLAY,
                    #         )
                    #     )

                    # matching_numbers = [
                    #     c for c in p.discard_queue if c.number == card_to_discard.number
                    # ]

                    # # We only want to give a hint if the first match should be played
                    # if card_to_discard == matching_numbers[0]:
                    #     hints.append(
                    #         Hint(
                    #             p,
                    #             Hint.TYPE_NUMBER,
                    #             card_to_discard.number,
                    #             card_to_discard,
                    #             purpose=Hint.PURPOSE_PLAY,
                    #         )
                    #     )



        # Next create hints to protect endangered cards
        for p in players:
            if p == self:
                continue
        return hints
