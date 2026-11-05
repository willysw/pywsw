import matplotlib.pyplot as plt
from rich.pretty import pprint as pp  # noqa: F401

from pywsw.analysis.beam import Beam
from pywsw.analysis.fem.load import UniformLoad

E = 1.6e6
I = 3.5 * 9.5**3 / 12
B = Beam(120, modulus=E, inertia=I)

res = B(UniformLoad(-10.0))

res.plot()

plt.show()
