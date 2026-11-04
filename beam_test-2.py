import matplotlib.pyplot as plt
import numpy as np
from rich.pretty import pprint as pp

from pywsw.analysis.fem import (
    Element,
    Node,
    dof,
    get_local_element_vectors,
    load,
    solve_system,
)
from pywsw.analysis.fem.types import (
    DOFType,
    ElementList,
    IndexType,
    LoadList,
    Mat,
    NodeList,
    Vec,
)

""" ╔══════════════════════════════════════════════════════════╗
    ║                    Problem Definition                    ║
    ╚══════════════════════════════════════════════════════════╝ """

elems: ElementList = [
    ((0, 1), Element("A", "B")),
    ((1, 2), Element("B", "C")),
    ((2, 3), Element("C", "D")),
]

nodes: NodeList = [
    Node(0.0),
    Node(1.0),
    Node(2.0),
    Node(3.0),
]

loads: LoadList = [
    [load.UniformLoad(-1.0)],
    [load.UniformLoad(-1.0)],
    [load.UniformLoad(-1.0)],
]

supports: dict[IndexType, Vec] = {
    0: (1.0, 0.0),
    1: (1.0, 0.0),
    2: (1.0, 0.0),
    3: (1.0, 0.0),
}

DOF: DOFType = dof.BeamDOF

""" ╔══════════════════════════════════════════════════════════╗
    ║                        Testing...                        ║
    ╚══════════════════════════════════════════════════════════╝ """

l = DOF.get_element_lengths(elems, nodes)
pp(l)

elem_K: tuple[Mat] = DOF.build_local_stiffness_matrices(
    elems,
    nodes=nodes,
    lengths=l,
)
pp(elem_K)

elem_Ffe: tuple[Vec] = DOF.build_local_fixed_end_vectors(
    elems,
    nodes,
    loads,
    lengths=l,
)
pp(elem_Ffe)

K: Mat = DOF.build_global_stiffness_matrix(
    elems,
    nodes,
    elem_matrices=elem_K,
)
pp(K)

Ffe: Vec = DOF.build_global_fixed_end_vector(
    elems,
    nodes,
    fixed_end_vecs=elem_Ffe,
)
pp(Ffe)

Ro, Zo = DOF.build_global_unknown_vectors(nodes, supports)
pp(Ro)
pp(Zo)

R, Z = solve_system(K, Zo, Ffe, Ro)
pp(R)
pp(Z)

ze = get_local_element_vectors(Z, [_t for _t, _ in elems], DOF.DOF)

x: Mat = np.asarray([np.linspace(0.0, _l, 100, dtype=float) for _l in l])
sols = [
    DOF.compute_internals(
        x[_i],
        ze[_i],
        length=l[_i],
        loads=loads[_i],
        material=_elem.material,
        section=_elem.section,
    )
    for _i, (_, _elem) in enumerate(elems)
]

x_o = np.concat([(0.0,), np.cumsum(l)])
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
for _ax in (ax1, ax2, ax3, ax4):
    _ax.grid(True, which="both")
    _ax.axhline(0, color="black")

for _xo, _x, _s in zip(x_o, x, sols):
    ax1.plot(_x + _xo, _s.Fx[0])
    ax3.plot(_x + _xo, _s.Fx[1])
    ax2.plot(_x + _xo, _s.Zx[1])
    ax4.plot(_x + _xo, _s.Zx[0])

plt.show()
