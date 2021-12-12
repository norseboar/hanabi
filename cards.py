from enum import Enum


class Suit(Enum):
    WHITE = "WHITE"
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    BLUE = "BLUE"
    RAINBOW = "RAINBOW"


class Card:
    def __init__(self, suit, number):
        self.suit = suit
        self.number = number
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
            assert (self.hinted_suit is None) or (self.hinted_suit == hint.value)
            assert hint.value == self.suit
            self.hinted_suit = hint.value
            return True

        if hint.type == Hint.TYPE_NUMBER and self.number == hint.value:
            assert (self.hinted_number is None) or (self.hinted_number == hint.value)
            assert hint.value == self.number
            self.hinted_number = hint.value
            return True

        return False


class Hint:
    TYPE_SUIT = "TYPE_SUIT"
    TYPE_NUMBER = "TYPE_NUMBER"

    PURPOSE_PLAY = "PURPOSE_PLAY"
    PURPOSE_PROTECT = "PURPOSE_PROTECT"

    def __init__(self, player, type, value, target_card=None, purpose=None):
        assert type == Hint.TYPE_SUIT or type == Hint.TYPE_NUMBER

        self.player = player
        self.type = type
        self.value = value
        self.target_card = target_card
        self.purpose = purpose
