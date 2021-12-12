from .player import Player


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
