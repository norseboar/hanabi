class Player:
    """Abstract class for Players. Any new strategy can inherit this."""

    def __init__(self, game, player_number, weights):
        self.game = game
        self.player_number = player_number
        self.weights = weights

    def __repr__(self):
        s = "Player {}\n".format(self.player_number)
        return s

    def add_card(self, card):
        """Called by Game whenever a card is added to a player's hand."""
        if not card:
            return
        self._add_card(card)

    def _add_card(self, card):
        pass

    def get_hand(self):
        """Called by Game and other players to see the cards a player has"""
        pass

    def take_turn(self):
        """Called by Game each time it is the player's turn"""
        pass

    def receive_hint(self, hint):
        """Called by Game each time another player gives the player a hint"""
        pass
