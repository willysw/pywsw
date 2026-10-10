from collections.abc import Iterable
from typing import Any

from numpy import asarray, ndarray

__all__ = ('parse_as_ndarray',)


def parse_as_ndarray(
        *args,
        scalar_dims:int=0
) -> ndarray | tuple[ndarray,...]:
    """ Parse the arguments as Numpy arrays.

    Parameters
    ----------
    *args
        Objects to be parsed as arrays. All objects must be compatible
        with `numpy.asarray()`.

    scalar_dims : int, keyword only, optional
        Determines how many dimensions a singular output array should have
        for passed scalar values. Defaults to 0.

    Returns
    -------
    ndarray | tuple[ndarray,...]
        Returns a tuple of ndarrays in the same order passed in `*args`.
        If no args are given, returns an empty tuple.

    Examples
    --------
        >>> parse_args_as_ndarray()
        None

        >>> parse_args_as_ndarray((1, 2, 3), 4.0, (4.0,))
        (ndarray([1, 2, 3]), ndarray(4.0), ndarray([4.0]))

        >>> parse_args_as_ndarray(4.0, scalar_dims=1)
        ndarray([4.0])

        >>> parse_args_as_ndarray(4.0, scalar_dims=2)
        ndarray([[4.0]])
    """
    out: list[ndarray] = []

    for argj in args:
        if isinstance(argj, ndarray):
            out.append(argj)
        elif isinstance(argj, Iterable):
            out.append(asarray(argj))
        else:
            outj: ndarray[Any] = asarray(argj)
            if scalar_dims > 0:
                outj = outj.reshape([1]*scalar_dims)
            out.append(outj)

    match len(out):
        case 0:
            return tuple(out)
        case 1:
            return out[0]
        case _:
            return tuple(out)
