# from . import QueuePlayer


# class DirectHintPlayer(QueuePlayer):
#     DISCARD_TO_PLAY = "DISCARD_TO_PLAY"
#     PLAY_TO_DISCARD = "PLAY_TO_DISCARD"
#     CARD_DEAD = "CARD_DEAD"
#     CARD_UNPLAYABLE = "CARD_UNPLAYABLE"
#     CARD_POTENTIALLY_PLAYABLE = "CARD_PLAYABLE"

#     def get_card_status(self, card):
#         played_stack = self.game.played_cards[card.suit]
#         last_number = played_stack[-1].number if played_stack else 0

#         if card.hinted_suit and card.hinted_number:
#             if card.number <= last_number:
#                 return self.CARD_DEAD
#             elif card.number > last_number + 1:
#                 return self.CARD_UNPLAYABLE
#         elif card.hinted_suit:
#             if last_number == 5:
#                 return self.CARD_DEAD
#         elif card.hinted_number:
#             lowest_playable_number = 6
#             for suit in self.game.suits:
#                 played_stack = self.game.played_cards[suit]
#                 last_number = played_stack[-1].number if played_stack else 0
#                 if last_number + 1 < lowest_playable_number:
#                     lowest_playable_number = last_number + 1
#             if card.number < lowest_playable_number:
#                 return self.CARD_DEAD
#         return self.CARD_POTENTIALLY_PLAYABLE

#     def find_hints(self, players):
#         hints = []
#         needed_cards = self.game.get_needed_cards()

#         all_play_queue = []
#         for p in players:
#             all_play_queue += p.play_queue

#         for p in players:
#             if p == self:
#                 continue
#             for card_to_discard in p.discard_queue:
#                 if (
#                     card_to_discard in all_play_queue
#                     or card_to_discard not in needed_cards
#                 ):
#                     continue

#                 matching_suits = [
#                     c for c in p.discard_queue if c.suit == card_to_discard.suit
#                 ]

#                 # We only want to give a hint if the first match should be played
#                 if card_to_discard == matching_suits[0]:
#                     hints.append(
#                         Hint(p, Hint.TYPE_SUIT, card_to_discard.suit, card_to_discard)
#                     )

#                 matching_numbers = [
#                     c for c in p.discard_queue if c.number == card_to_discard.number
#                 ]

#                 # We only want to give a hint if the first match should be played
#                 if card_to_discard == matching_numbers[0]:
#                     hints.append(
#                         Hint(
#                             p, Hint.TYPE_NUMBER, card_to_discard.number, card_to_discard
#                         )
#                     )
#         return hints


# class HelpfulDirectPlayer(DirectHintPlayer):
#     def take_turn(self):
#         Player.take_turn(self)

#         needy_players = [p for p in self.game.players if not p.play_queue]
#         needy_hints = self.find_hints(needy_players)
#         all_hints = self.find_hints(self.game.players)

#         if self.game.hints > 0 and needy_hints:
#             self.game.give_hint(needy_hints[0])
#         elif self.play_queue:
#             self.play_from_hand()
#         elif self.game.hints > 0 and all_hints:
#             self.game.give_hint(all_hints[0])
#         else:
#             self.discard_from_hand()


# class SmartHints1Player(DirectHintPlayer):
#     def sort_hints(self, hints):
#         def score_hint(hint):
#             score = 0
#             score += (5 - len(hint.player.play_queue)) * 100

#             relative_position = (
#                 hint.player.player_number - self.player_number
#             ) % self.game.num_players
#             score += (self.game.num_players - relative_position) * 1000

#             return score

#         return sorted(hints, key=score_hint, reverse=True)


# class SmartHints2Player(DirectHintPlayer):
#     def sort_hints(self, hints):
#         def score_hint(hint):
#             score = 0
#             score += (5 - len(hint.player.play_queue)) * 1000

#             relative_position = (
#                 hint.player.player_number - self.player_number
#             ) % self.game.num_players
#             score += (self.game.num_players - relative_position) * 100

#             return score

#         return sorted(hints, key=score_hint, reverse=True)


# class SmartHints3Player(DirectHintPlayer):
#     def sort_hints(self, hints):
#         def score_hint(hint):
#             score = 0
#             score += (5 - len(hint.player.play_queue)) * 1000

#             relative_position = (
#                 hint.player.player_number - self.player_number
#             ) % self.game.num_players
#             score += (self.game.num_players - relative_position) * 100

#             score += (5 - hint.target_card.number) * 10000

#             return score

#         return sorted(hints, key=score_hint, reverse=True)


# class SmartHints4Player(DirectHintPlayer):
#     def sort_hints(self, hints):
#         def score_hint(hint):
#             score = 0
#             score += (5 - len(hint.player.play_queue)) * 100

#             relative_position = (
#                 hint.player.player_number - self.player_number
#             ) % self.game.num_players
#             score += (self.game.num_players - relative_position) * 1000

#             score += (5 - hint.target_card.number) * 10000

#             return score

#         return sorted(hints, key=score_hint, reverse=True)


# class ProtectCardsPlayer(SmartHints3Player):
#     def find_hints(self, players):
#         hints = []
#         needed_cards = self.game.get_needed_cards()

#         all_play_queue = []
#         for p in players:
#             all_play_queue += p.play_queue

#         for p in players:
#             if p == self:
#                 continue
#             for card_to_discard in p.discard_queue:
#                 if card_to_discard in all_play_queue:
#                     continue

#                 # First create hints for cards that should be played
#                 if card_to_discard in needed_cards:
#                     matching_suits = [
#                         c for c in p.discard_queue if c.suit == card_to_discard.suit
#                     ]

#                     # We only want to give a hint if the first match should be played
#                     if card_to_discard == matching_suits[0]:
#                         hints.append(
#                             Hint(
#                                 p,
#                                 Hint.TYPE_SUIT,
#                                 card_to_discard.suit,
#                                 card_to_discard,
#                                 purpose=Hint.PURPOSE_PLAY,
#                             )
#                         )

#                     matching_numbers = [
#                         c for c in p.discard_queue if c.number == card_to_discard.number
#                     ]

#                     # We only want to give a hint if the first match should be played
#                     if card_to_discard == matching_numbers[0]:
#                         hints.append(
#                             Hint(
#                                 p,
#                                 Hint.TYPE_NUMBER,
#                                 card_to_discard.number,
#                                 card_to_discard,
#                                 purpose=Hint.PURPOSE_PLAY,
#                             )
#                         )
#                 elif (
#                     self.game.cards_remaining[card_to_discard.suit][
#                         card_to_discard.value
#                     ]
#                     <= 1
#                 ):
#                     assert (
#                         self.game.cards_remaining[card_to_discard.suit][
#                             card_to_discard.value
#                         ]
#                         == 1
#                     )
#                     matching_suits = [
#                         c for c in p.discard_queue if c.suit == card_to_discard.suit
#                     ]

#                     # We only want to give a hint if nothing can be played

#                     ####### NEEDS WORK ######

#                     # if card_to_discard == matching_suits[0]:
#                     #     hints.append(
#                     #         Hint(
#                     #             p,
#                     #             Hint.TYPE_SUIT,
#                     #             card_to_discard.suit,
#                     #             card_to_discard,
#                     #             purpose=Hint.PURPOSE_PLAY,
#                     #         )
#                     #     )

#                     # matching_numbers = [
#                     #     c for c in p.discard_queue if c.number == card_to_discard.number
#                     # ]

#                     # # We only want to give a hint if the first match should be played
#                     # if card_to_discard == matching_numbers[0]:
#                     #     hints.append(
#                     #         Hint(
#                     #             p,
#                     #             Hint.TYPE_NUMBER,
#                     #             card_to_discard.number,
#                     #             card_to_discard,
#                     #             purpose=Hint.PURPOSE_PLAY,
#                     #         )
#                     #     )

#         # Next create hints to protect endangered cards
#         for p in players:
#             if p == self:
#                 continue
#         return hints
