import numpy as np

from game import Card, Hand


class FractionMatrix(np.ndarray):

    def __new__(cls, input_array, denominator: int):
        obj = np.asarray(input_array).view(cls)
        obj.denominator = denominator
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.denominator = getattr(obj, 'denominator', 1)

    def __sub__(self, other):
        common_multiple = np.lcm(self.denominator, other.denominator)
        self_array = self.view(np.ndarray) * (common_multiple // self.denominator)
        other_array = other.view(np.ndarray) * (common_multiple // other.denominator)
        return FractionMatrix(self_array - other_array, common_multiple)

    def __add__(self, other):
        common_multiple = np.lcm(self.denominator, other.denominator)
        self_array = self.view(np.ndarray) * (common_multiple // self.denominator)
        other_array = other.view(np.ndarray) * (common_multiple // other.denominator)
        return FractionMatrix(self_array + other_array, common_multiple)

    def __mul__(self, other):
        raise NotImplementedError

    def __truediv__(self, other):
        raise NotImplementedError

    def make_proba(self):
        # I should check the complexity of this operation
        # And actually, we can set the denominator to the size of the deck
        self.denominator = int(np.sum(self))
        gcd = np.gcd.reduce(self.flatten())
        self.__ifloordiv__(gcd)
        self.denominator = self.denominator // gcd


    def is_proba(self):
        return int(np.sum(self)) == self.denominator


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