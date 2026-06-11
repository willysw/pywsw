import math # noqa
import pytest

from pywsw.codes.aci318.ch09.reinf_limits import *

@pytest.fixture
def beam_def_1():
    yield dict(
        b_w = 8.0,
        d = 16.0,
        f_c = 3000.0,
        f_y = 60000.0
    )

@pytest.fixture
def beam_def_2(beam_def_1):
    beam_def_1.update(
        E_s = 30.0e6,
        e_c = -0.003,
        beta_1 = 0.85
    )
    yield beam_def_1


def test_as_max(beam_def_2):
    a_max = A_s_max_9_3_3_1(**beam_def_2)
    assert f'{a_max:.4f}' == '2.0400'


def test_as_min(beam_def_1):
    a_min = A_s_min_9_6_1_2(**beam_def_1)
    assert f'{a_min:.4f}' == '0.3505'
