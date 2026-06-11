__all__ = ['make_arraylike', 'set_units']

from collections.abc import Sequence, Iterable
from functools import wraps
from inspect import signature
import numpy as np
from typing import Callable


def make_arraylike(*args) -> Callable:
    def make_arraylike_decorator(func):
        func_sig = signature(func)
        params = set()
        for i in (arg.split() for arg in args if isinstance(arg, str)):
            params.update(i)

        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            bound_args = func_sig.bind(*func_args, **func_kwargs)
            for param in params:
                if param in bound_args.arguments:
                    if not np.isscalar(bound_args.arguments[param]):
                        bound_args.arguments[param] = np.asarray(bound_args.arguments[param])
                elif param in bound_args.kwargs:
                    if not np.isscalar(bound_args.kwargs[param]):
                        bound_args.kwargs[param] = np.asarray(bound_args.kwargs[param])
            return func(*bound_args.args, **bound_args.kwargs)
        return wrapper

    return make_arraylike_decorator


def set_units(
        ret_units: str|None|Iterable[str|None],
        arg_units: Iterable[str|None],
        ) -> Callable:
    """
    Store units for use with ``pint.wraps()``.

    Parameters
    ----------
    ret_units: str|None or Iterable[str|None]
        Unit string or sequence of unit strings.
    arg_units: Iterable[str|None]
        Sequence of units strings.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        if isinstance(ret_units, str):
            ret_units_out = ret_units
        elif ret_units is None:
            ret_units_out = None
        elif isinstance(ret_units, Iterable):
            ret_units_out = tuple(ret_units)
        else:
            raise TypeError(f'Unknown return unit type {type(ret_units)}: {ret_units}') # noqa
        setattr(wrapper, 'ret_units', ret_units_out)
        setattr(wrapper, 'arg_units', tuple(arg_units))
        setattr(wrapper, 'pint_args', (ret_units_out, tuple(arg_units)))
        return wrapper
    return decorator


if __name__ == '__main__':
    @set_units('lbf', ['lbf/ft^2', None])
    def some_function(x, y):
        return x * y
    print(some_function.ret_units.__repr__())
    print(some_function.arg_units.__repr__())
    print(some_function.pint_args.__repr__())

