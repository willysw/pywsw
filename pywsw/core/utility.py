from numpy.typing import ArrayLike
from numpy import isscalar, asarray


__all__ = ['parse_array_like']


def parse_array_like(*args) -> ArrayLike[float]:
    for arg in args:
        if isscalar(arg):
            yield arg
        else:
            yield asarray(arg)
