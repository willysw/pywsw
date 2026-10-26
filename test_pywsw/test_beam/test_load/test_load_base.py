import pytest

from pywsw.analysis.beam.load import LoadBase


def test_make_LoadBase_instance():
    with pytest.raises(TypeError):
        # pyrefly: ignore[bad-instantiation]
        _ = LoadBase()
