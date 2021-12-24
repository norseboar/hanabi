from enum import Enum


class Suit(Enum):
    WHITE = "WHITE"
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    BLUE = "BLUE"
    RAINBOW = "RAINBOW"


class Card:
    def __init__(self, suit, number, game):
        self.suit = suit
        self.number = number
        self.game = game
        self.hinted_suit = None
        self.hinted_number = None

    def __repr__(self):
        return "{} {}".format(self.suit, self.number)

    def match_hint(self, hint):
        if hint.type == Hint.TYPE_SUIT:
            return self.suit == hint.value
        elif hint.type == Hint.TYPE_NUMBER:
            return self.number == hint.value

    def apply_hint(self, hint):
        if hint.type == Hint.TYPE_SUIT and self.suit == hint.value:
            self.game.assert_(
                (self.hinted_suit is None) or (self.hinted_suit == hint.value)
            )
            self.hinted_suit = hint.value
            return True

        if hint.type == Hint.TYPE_NUMBER and self.number == hint.value:
            self.game.assert_(
                (self.hinted_number is None) or (self.hinted_number == hint.value)
            )
            self.game.assert_(hint.value == self.number)
            self.hinted_number = hint.value
            return True

        return False


class Hint:
    TYPE_SUIT = "TYPE_SUIT"
    TYPE_NUMBER = "TYPE_NUMBER"

    def __repr__(self):
        return "To {}: {} {} {} | Targeting {}".format(
            self.player.player_number,
            self.type,
            self.value,
            self.purpose,
            self.target_card,
        )

    def __init__(self, player, type, value, game, target_card=None, purpose=None):
        game.assert_(type == Hint.TYPE_SUIT or type == Hint.TYPE_NUMBER)

        self.player = player
        self.type = type
        self.value = value
        self.game = game
        self.target_card = target_card
        self.purpose = purpose
