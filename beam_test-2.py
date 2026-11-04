import numpy as np  # noqa: F401
from rich.pretty import pprint as pp

from pywsw.analysis.beam import (
    Element,
    Node,
    dof,
    load,
    solve_system,
)
from pywsw.analysis.beam.types import (
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
