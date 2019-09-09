"""This module contains a readable archive of the best codes."""

import json
import os

from jeweler.io import Archiver

__all__ = [
    'best'
]


def best(L, objective_function, weight):
    """Access best codes from previous searches.

    >>> best(10, 'spectral_flatness', 5)
    [0, 0, 0, 0, 1, 1, 0, 1, 1, 1]
    """
    f = Archiver(output_dir=os.path.dirname(__file__))
    return f.fetch(
        L=L,
        objective_function=objective_function,
        weight=weight
    )['code']


if __name__ == "__main__":
    import doctest
    doctest.testmod()
