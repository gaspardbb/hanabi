from typing import List, Any

import numpy as np

INIT_ARRAY = np.array([[3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1]], dtype='int8')


def check_isin(value, boundaries):
    """
    A simple function to check if a value is in the desired boundaries.

    Args:
        value: the value to check
        boundaries: a tuple of boundaries

    Raises:
        ValueError: if the value is not in the boundaries.
        AssertionError: if the boundaries are ill-defined.
    """
    assert len(boundaries) == 2, "Boundaries should be a length-2 tuple or list."
    assert boundaries[0] <= boundaries[1]
    if not boundaries[0] <= value <= boundaries[1]:
        raise ValueError("%s is not in the provided boundaries: %s - %s." % (value, boundaries[0], boundaries[1]))


def check_iscard(card):
    """
    Simple function to check we have a `Card` object.

    Args:
        card: the card to be tested.

    Raises:
         ValueError if not instance of `Card`.
    """
    if not isinstance(card, Card):
        raise ValueError("You need to pass a `Card` as a parameter! Got %s." % type(card))


def check_ishand(hand):
    """
    Simple function to check we have a `Hand` object.

    Args:
        hand: the hand to be tested.

    Raises:
         ValueError if not instance of `Hand`.
    """
    if not isinstance(hand, Hand):
        raise ValueError("You need to pass a `Hand` as a parameter! Got %s." % type(hand))


def make_iterable(value):
    """
    A simple function to turn any value in a list.

    Args:
        value: something to turn in a list. If it's already iterable, nothing is changed.

    Returns:
        A list.
    """
    if not (isinstance(value, list) or isinstance(value, tuple)):
        return [value]
    return value


class Information:

    def __init__(self, info_type: str, data: int, negative: bool):
        if info_type == "color":
            self.type = info_type
            self.is_color = True
            self.is_value = False
        elif info_type == "value":
            self.type = info_type
            self.is_color = False
            self.is_value = True
        else:
            raise ValueError("Type of information must be `color` or `value`. Got: %s." % info_type)

        check_isin(data, (0, 4))
        self.data = data
        self.negative = negative


class Card:
    COLOR = ["B", "W", "R", "Y", "G"]

    def __init__(self, color: int, value: int, hand):
        check_isin(color, (0, 4))
        check_isin(value, (0, 4))
        check_ishand(hand)

        self.hand = hand
        self.player_id = hand.id
        self.color = color
        self.value = value
        self.information = np.ones((5, 5), dtype='bool')

    def __getitem__(self, item):
        return self.information[item]

    def __setitem__(self, key, value):
        self.information[key] = value

    def __repr__(self):
        return "%s%s" % (Card.COLOR[self.color], self.value)

    def add_information(self, info: Information):
        """
        Add information on a Card.

        Args:
            info: an Information object.

        This function puts rows (if information is about colors) or columns (if information is about values) to 0.
        """
        if info.is_color:
            if info.negative:
                self[info.data, :] = 0
            else:
                self[:info.data, :] = 0
                self[info.data + 1:, :] = 0
        else:
            if info.negative:
                self[:, info.data] = 0
            else:
                self[:, :info.data] = 0
                self[:, info.data + 1:] = 0

    def probabilities(self, rational=False):
        """
        Get the probability of having each card in the game.

        Args:
            rational: if True, returns a tuple of (int array, int). Otherwise, returns the ratio of these two
            quantities as a float array.

        Returns:
            A numpy array.
        """
        state = self.information * Game.states[self.player_id]
        total = np.sum(state)
        if rational:
            return state, total
        else:
            return state / total

    def determined(self):
        """
        Tell if the card has be determined or not (a single color & a single value are possible).

        Returns:
            A boolean.
        """
        probabilities, _ = self.probabilities(rational=True)
        n_possible = np.where(probabilities != 0)[0].size
        assert n_possible != 0
        if n_possible == 1:
            return True
        else:
            return False

    def well_predicted(self):
        """
        Tells if a card has been well predicted. To do that, it first needs to be determined.

        Returns:
            A boolean. True if it has been determined and the color and value predicted match. False otherwise.
        """
        if self.determined():
            index_predicted = np.argwhere(self.information == 1)[0]
            if index_predicted[0] == self.color and index_predicted[1] == self.value:
                return True
        return False

    def most_likely(self, return_proba: False):
        """
        Tell what is the card the most likely to be.

        Args:
            return_proba: if True, returns the probability too. Otherwise, simply returns a tuple containing the
            indices of the most likely identities.

        Returns:
            A tuple (if return_proba) or a (tuple, float).
        """
        probabilities, total = self.probabilities(rational=True)
        max_probas = np.max(probabilities)
        arg_probas = np.argwhere(probabilities == max_probas)

        if return_proba:
            return arg_probas, max_probas / total
        else:
            return arg_probas


class Hand:

    cards: List[Card]

    def __init__(self, player_id):
        self.id = player_id
        self.cards = []

    def add_cards(self, cards):
        cards = make_iterable(cards)
        for card in cards:
            check_iscard(card)
            self.cards.append(card)

    def __repr__(self):
        return " ".join([str(card) + " " for card in self.cards])

class Game:
    """
    This is the class which manages everything which happens in the area of the game. In the end, it should have
    multiple array;
    . All the cards which were discarded or played
    . All the cards in each player's hands
    . = All the cards which remain in the deck
    This class should know everything.
    """

    # this variable contains every cards out of the deck, to make sure we're not playing the same card twice.
    deck = INIT_ARRAY.copy()
    # these variables are the game seen from player 0 and player 1's perspective.
    # i.e it's the initial array
    #            - every cards played
    #            - every cards discarded
    #            - every cards on the other players' hand.
    states = []
    # thus, at all time, we should have states >= deck
    players: List[Hand] = []

    @staticmethod
    def deal_card(card):
        """
        Function to give a card to a player. It's the only way a card is moving out of the deck.

        Args:
            card:  a valid Card object. It contains an attribute 'Hand', which refers to a valid player.

        Raises:
            ValueError:
                . If the player id is not valid
                . If card is not an instance of Card
                . If the card is not part of the deck anymore
        """
        check_iscard(card)
        player_id = card.hand.id
        check_isin(player_id, (0, len(Game.players)))

        if Game.deck[card.color, card.value] == 0:
            raise ValueError("You're attempting to give a card which is not part of the deck! %s" % card)

        # We put it out of the deck
        Game.deck[card.color, card.value] -= 1

        # We make the other player aware of that
        for i in range(len(Game.states)):
            if i != player_id:
                Game.states[i][card.color, card.value] -= 1

        # It it the only way a card is moving out of the deck. So we must always have Game.states >= Game.deck
        # Finally, we add it to the proper player's hand.
        Game.players[player_id].add_cards(card)

    @staticmethod
    def deal_hand(player_id, n=5):
        check_isin(player_id, (0, len(Game.players)))
        for i in range(n):
            card = Game.random_card(player_id=player_id)
            Game.deal_card(card)

    @staticmethod
    def add_player():
        """
        Add a player to the game.
        """
        Game.players.append(Hand(len(Game.players)))
        Game.states.append(INIT_ARRAY.copy())

    @staticmethod
    def random_card(player_id: int):
        probabilities = Game.deck / np.sum(Game.deck)
        sample = np.random.choice(probabilities.size, size=1, p=probabilities.flatten())
        sample = int(sample)
        return Card(color=sample // 5, value=sample % 5, hand=Game.players[player_id])


if __name__ == '__main__':
    Game.add_player()
    Game.add_player()
    Game.deal_hand(0, n=5)
    Game.deal_hand(1, n=5)
    # Game.players[0].cards[0].add_information(Information("color", Game.players[0].cards[0].color, False))
    print("Player 0 : \n%s" % Game.players[0])
    print("Player 1 : \n%s" % Game.players[1])
    print("State  0 : \n%s" % Game.states[0])
    print("State  1 : \n%s" % Game.states[1])
    print("Deck : \n%s" % Game.deck)
    print("Proba. for first card of player 0 : \n%s / %s" % Game.players[0].cards[0].probabilities(rational=True))
