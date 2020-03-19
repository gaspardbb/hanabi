"""
This file focuses on computing the probability for a single player, who does not have access to its hand.
We avoid using the omniscient class Game.

Most simple would have been to recode everything...
"""
from typing import Iterable

import numpy as np

from game import Information, Hand, Card
from utils import check_isin

INIT_ARRAY = np.array([[3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1],
                       [3, 2, 2, 2, 1]], dtype='int32')


class OnePlayer:

    def __init__(self, n_cards=5):
        """Initialize the hand of the player."""
        self.states = INIT_ARRAY.copy()
        self.hand = Hand(0)

        for _ in range(n_cards):
            new_card = Card(color=Card.UNK, value=Card.UNK, hand=self.hand)
            self.hand.add_card(new_card, game_start=True)

    def see_card(self, color, value):
        """See a new card, either from the other hand or one you just picked."""
        check_isin(color, (0, 4))
        check_isin(value, (0, 4))
        self.states[color, value] -= 1
        assert self.states[color, value] >= 0

    def play_card(self, card_index, color: int, value: int):
        """Play one of your card."""
        check_isin(color, (0, 4))
        check_isin(value, (0, 4))

        card = self.hand.cards[card_index]

        # Update states
        self.see_card(color, value)

        # The card is now determined (for computing the probas of the others)
        card.color = color
        card.value = value
        card.played = True
        self.hand.remove_card(card)

    def add_information(self, card_index: int or Iterable[int], info: Information):
        """Receive an information on one's hand."""
        self.hand.add_information(card_index, info)

    def add_card(self):
        """Add an unknown card in the hand."""
        new_card = Card(color=Card.UNK, value=Card.UNK, hand=self.hand)
        self.hand.add_card(new_card)

    def card_probability(self, card_index, return_denominator=True):
        """Necessary to recode this function to pass special player_state (and not fetch the Game's player state)."""
        return self.hand.cards[card_index].probabilities(return_denominator, player_state=self.states)


if __name__ == '__main__':
    op = OnePlayer()
    # See three <1 Blue>
    op.see_card(0, 0)
    op.see_card(0, 0)
    op.see_card(0, 0)
    # And one <2 Blue>
    op.see_card(0, 1)

    # Learn that your first two cards are blue
    op.add_information((0, 1), Information("color", 0, False))

    # Get probabilities of each card
    for i in range(5):
        print(f"{i}: {op.card_probability(i)}")

    # Play the third and learn its a 5 white
    op.play_card(2, 1, value=4)
    op.add_card()

    print("AFTER PLAYING")
    for i in range(5):
        print(f"{i}: {op.card_probability(i)}")