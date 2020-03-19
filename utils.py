import numpy as np


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


def pretty_probability(array: np.ndarray):
    assert array.shape == (5, 5)
    colors = ["Bl", "Wh", "Re", "Ye", "Gr"]
    result = "\t1\t2\t3\t4\t5\n"
    result += "\n"
    for i in range(5):
        result += colors[i]
        for j in range(5):
            result += "\t"+str(array[i, j])
        result += "\n"
    return result
    # new_array = np.zeros((6, 6), dtype="object")
    # new_array[0, 0] = " "
    # new_array[1:, 0] = ["Bl", "Wh", "Re", "Ye", "Gr"]
    # new_array[0, 1:] = [1, 2, 3, 4, 5]
    # new_array[1:, 1:] = array
    # return new_array.__repr__()