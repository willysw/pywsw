from itertools import count

import numpy as np
from rich import print

from pywsw.analysis.beam import (
    Arr,
    LoadType,
    Mat,
    Vec,
    add_to_global_matrix,
    add_to_global_vector,
    load,
    solve_system,
)
from pywsw.analysis.beam.dof import BeamDOF

l = [1.0, 1.0]
Eb, Ib = 1.0, 1.0
Ke: list[Mat] = [BeamDOF.stiffness_matrix(li, E_b=Eb, I_b=Ib) for li in l]
w: list[LoadType] = [
    load.UniformLoad(-0.3),
    load.UniformLoad(-0.7),
]
fe: list[Vec] = [BeamDOF.fixed_end_force(li, w) for li in l]

z = [0, np.nan, 0, np.nan, 0, np.nan]
r = [np.nan, 0, np.nan, 0, np.nan, 0]

n = 6
K: Mat = np.zeros((n, n), dtype=float)
f: Vec = np.zeros((n,), dtype=float)
for n0, n1, Ki, fi in zip(count(0), count(1), Ke, fe):
    K = add_to_global_matrix(n0, n1, K, Ki)
    f = add_to_global_vector(n0, n1, f, fi)

rs, zs = solve_system(K, z, f, r)

zel = zs[0:4]
fel = np.linalg.matmul(Ke[0], zel) + fe[0]

xe: list[Vec] = [np.linspace(0.0, li, 10) for li in l]
ome: list[list[Arr]] = [
    [wj.omega(xej, nk) for nk in (0, 1, 2, 3)] for wj, xej in zip(w, xe)
]

with np.printoptions(precision=2):
    print(ome)
