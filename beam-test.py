from collections import defaultdict
from collections.abc import Hashable, Iterable, Mapping
from typing import Any, TypeVar

import numpy as np
from rich import print

from pywsw.analysis.beam import (
    Element,
    LoadType,
    Mat,
    Node,
    Vec,
    add_to_global_matrix,
    add_to_global_vector,
    get_empty_global_matrix,
    get_local_element_vector,
    load,
    solve_system,
)
from pywsw.analysis.beam.dof import BeamDOF
from pywsw.analysis.beam.types import DOFType

_NE = TypeVar("_NE", bound=Element | Node)
type ItemDB[_NE] = Mapping[Hashable, _NE]
type ElemDB = ItemDB[Element]
type NodeDB = ItemDB[Node]
type TagMap = Mapping[Hashable, int]
type InvTagMap = Mapping[int, Hashable]
type LoadList = list[LoadType, Iterable[Hashable]]
type LoadMap = Mapping[Hashable, tuple[LoadType, ...]]
type SupportDB = Mapping[Hashable, Iterable[float]]
type MatMap = Mapping[Hashable, Mat]
type VecMap = Mapping[Hashable, Vec]


def build_map(d: Mapping[Hashable, Any]) -> TagMap:
    return {_k: _idx for _idx, _k in enumerate(d.keys())}


def invert_map(m: TagMap) -> InvTagMap:
    return {_idx: _k for _k, _idx in m.items()}


def build_list(items: ItemDB[_NE], item_map: TagMap) -> list[_NE]:
    inv_map = invert_map(item_map)
    return [items[inv_map[_idx]] for _idx in sorted(inv_map.keys())]


def build_load_map(loads: LoadList) -> LoadMap:
    load_map: dict[Hashable, list[LoadType]] = defaultdict(list)
    for _load, _elem_ids in loads:
        for _elem_id in _elem_ids:
            load_map[_elem_id].append(_load)
    return {_k: tuple(_v) for _k, _v in load_map.items()}


def build_element_stiffness_matrix_map(
    elems: ElemDB,
    nodes: NodeDB,
    nodemap: TagMap,
    dof: DOFType,
) -> MatMap:
    map_out: MatMap = {}
    for _k, _elem in elems.items():
        node0 = nodes[_elem.node0]
        _id0 = nodemap[_elem.node0]
        node1 = nodes[_elem.node1]
        _id1 = nodemap[_elem.node1]
        length = node0.distance(node1)
        map_out[_k] = dof.stiffness_matrix(length, E_b=_elem.EI)
    return map_out


def build_element_fixed_end_force_map(
    elems: ElemDB,
    nodes: NodeDB,
    nodemap: TagMap,
    loadmap: LoadMap,
    dof: DOFType,
) -> VecMap:
    map_out: VecMap = {}
    for _k, _elem in elems.items():
        node0 = nodes[_elem.node0]
        _id0 = nodemap[_elem.node0]
        node1 = nodes[_elem.node1]
        _id1 = nodemap[_elem.node1]
        length = node0.distance(node1)
        map_out[_k] = dof.fixed_end_force(length, loadmap[_k])
    return map_out


# Build K matrix
def build_stiffness_matrix(
    elems: ElemDB,
    elem_K_map: MatMap,
    nodemap: TagMap,
    dof: DOFType,
) -> Mat:
    K: Mat = get_empty_global_matrix(len(nodes), dof.DOF)
    for _k, _elem in elems.items():
        _id0 = nodemap[_elem.node0]
        _id1 = nodemap[_elem.node1]
        K: Mat = add_to_global_matrix(_id0, _id1, K, elem_K_map[_k])
    return K


def build_fixed_end_force_vector(
    elems: ElemDB,
    elem_Ffe_map: VecMap,
    nodemap: TagMap,
    dof: DOFType,
) -> Vec:
    Ffe: Vec = np.zeros((len(nodes) * dof.DOF,), dtype=float)
    for _k, _elem in elems.items():
        _id0 = nodemap[_elem.node0]
        _id1 = nodemap[_elem.node1]
        Ffe: Vec = add_to_global_vector(_id0, _id1, Ffe, elem_Ffe_map[_k])
    return Ffe


def build_unknown_r_z_vectors(
    nodes: NodeDB, nodemap: TagMap, supports: SupportDB, dof: DOFType
) -> tuple[Vec, Vec]:
    R: Vec = np.full((len(nodes) * dof.DOF,), 0, dtype=float)
    for _k, _supps in supports.items():
        _n0 = nodemap[_k]
        I0: slice = slice(dof.DOF * (_n0), dof.DOF * (_n0 + 1), 1)
        R[I0] += _supps
    return np.where(R, np.nan, 0), np.where(R, 0, np.nan)


# Problem Definition
elems: ElemDB = {  # Spans
    "e3": Element("n1", "n6", EI=1.0),
    "e9": Element("n6", "n3", EI=1.0),
    "e1": Element("n3", "n2", EI=1.0),
}
nodes: NodeDB = {  # Nodes
    "n1": Node(0.0),
    "n6": Node(1.0),
    "n3": Node(2.5),
    "n2": Node(3.5),
}
supports: SupportDB = {  # Support Conditions
    "n1": (1.0, 0.0),
    "n3": (1.0, 0.0),
    "n6": (1.0, 0.0),
    "n2": (1.0, 0.0),
}
loads: LoadList = [  # Loads List
    (load.UniformLoad(-2.0), ("e3", "e1")),
    (load.UniformLoad(-1.0), ("e9",)),
]

# Build element, node, and load mappings and lists
elem_map: TagMap = build_map(elems)
elem_list = build_list(elems, elem_map)

node_map: TagMap = build_map(nodes)
node_list = build_list(nodes, node_map)

load_map: LoadMap = build_load_map(loads)

# Problem Parameters
n_nodes = len(node_list)
n_elems = len(elem_list)

# Element stiffness matrices and fixed-end-force vectors
K_map: MatMap = build_element_stiffness_matrix_map(
    elems, nodes, node_map, BeamDOF
)
Ffe_map: VecMap = build_element_fixed_end_force_map(
    elems, nodes, node_map, load_map, BeamDOF
)

# Build global stiffness matrix
K: Mat = build_stiffness_matrix(elems, K_map, node_map, BeamDOF)
print("K Matrix")
print(K, "\n")

# Build fixed force vector
Ffe: Vec = build_fixed_end_force_vector(elems, Ffe_map, node_map, BeamDOF)
print("Ffe Vector")
print(Ffe, "\n")

# Build input Z and R vectors:
Ru, Zu = build_unknown_r_z_vectors(nodes, node_map, supports, BeamDOF)
print("Zu Vector")
print(Zu, "\n")
print("Ru Vector")
print(Ru, "\n")

# Solve the system
R, Z = solve_system(K, Zu, Ffe, Ru)
print("Z Vector")
print(Z, "\n")
print("R Vector")
print(R, "\n")

# Calculate element internal end forces:
Zi_map: VecMap = {
    _k: get_local_element_vector(
        Z, node_map[_elem.node0], node_map[_elem.node1], BeamDOF.DOF
    )
    for _k, _elem in elems.items()
}
print("Zi_map")
print(Zi_map)

Ri_map: VecMap = {
    _k: np.matmul(
        np.diagflat((-1, -1, 1, 1)),
        np.matmul(K_map[_k], Zi_map[_k]) + Ffe_map[_k],
    )
    for _k, _elem in elems.items()
}
with np.printoptions(precision=3):
    print("Ri_map")
    print(Ri_map)

# Compute Element Curves
import matplotlib.pyplot as plt

length_map = {
    _k: nodes[_elem.node0].distance(nodes[_elem.node1])
    for _k, _elem in elems.items()
}
start_map = {_k: nodes[_elem.node0].x for _k, _elem in elems.items()}
print(length_map)
X_map: VecMap = {_k: np.linspace(0.0, _l, 100) for _k, _l in length_map.items()}
V_map: VecMap = {
    _k: Ri_map[_k][0]
    + np.sum([_load.omega(X_map[_k], 0) for _load in load_map[_k]], axis=0)
    for _k in elems
}
M_map: VecMap = {
    _k: Ri_map[_k][1]
    + X_map[_k] * V_map[_k]
    - np.sum([_load.omega(X_map[_k], 1) for _load in load_map[_k]], axis=0)
    for _k in elems
}
Q_map: VecMap = {
    _k: Zi_map[_k][1]
    + M_map[_k] * X_map[_k] / (_elem.EI)
    - (V_map[_k] * X_map[_k] ** 2) / (2 * _elem.EI)
    + np.sum([_load.omega(X_map[_k], 2) for _load in load_map[_k]], axis=0)
    / (2 * _elem.EI)
    for _k, _elem in elems.items()
}
U_map: VecMap = {
    _k: Zi_map[_k][0]
    + Q_map[_k] * X_map[_k]
    - (M_map[_k] * X_map[_k] ** 2) / (2 * _elem.EI)
    + (V_map[_k] * X_map[_k] ** 3) / (6 * _elem.EI)
    - np.sum([_load.omega(X_map[_k], 3) for _load in load_map[_k]], axis=0)
    / (6 * _elem.EI)
    for _k, _elem in elems.items()
}

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
for _ax in (ax1, ax2, ax3, ax4):
    _ax.grid(True, which="both")
    _ax.axhline(0.0, color="black")

for _k in elems:
    ax1.plot(X_map[_k] + start_map[_k], V_map[_k])
    ax3.plot(X_map[_k] + start_map[_k], M_map[_k])
    ax2.plot(X_map[_k] + start_map[_k], Q_map[_k])
    ax4.plot(X_map[_k] + start_map[_k], U_map[_k])

plt.show()
