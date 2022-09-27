from math import fabs
import os
import json
import copy

from compas.geometry import Line
from compas.geometry import Cylinder
from compas.utilities import remap_values

from compas_bender.datastructures import BendNetwork
from compas_bender.bender import bend_splines

from compas_view2.app import App
from compas_view2.objects import Collection

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "..", "data")

FILE_I = os.path.join(DATA, "paper", "arch.bender-in")
FILE_O = os.path.join(DATA, "paper", "arch.bender-out")

# ==============================================================================
# Network from file
# ==============================================================================

with open(FILE_I, "r") as f:
    data = json.load(f)

network = BendNetwork.from_data(data["network"])

splines = copy.deepcopy(data["splines"])
cables = copy.deepcopy(data["cables"])

# ==============================================================================
# Spline parameters
# ==============================================================================

splines[0]["E"] = 30
splines[0]["radius"] = 10
splines[0]["thickness"] = 10

for key, attr in network.edges(True):
    attr["linit"] = 0

# ==============================================================================
# Bend
# ==============================================================================

bend_splines(
    network,
    cables,
    splines,
    config={"kmax": 5000, "tol1": 1e-2, "tol2": 1e-1, "tol3": 1e-4},
)

# ==============================================================================
# Export
# ==============================================================================

with open(FILE_O, "w") as f:
    data["network"] = network.to_data()
    json.dump(data, f)

# ==============================================================================
# Viz
# ==============================================================================

viewer = App()

radii = [fabs(f) for f in network.edges_attribute("f")]
radii = remap_values(radii, 0.01, 0.2)
pipes = []
pipe_properties = []
for index, edge in enumerate(network.edges()):
    line = network.edge_line(edge)
    force = network.edge_attribute(edge, "f")
    color = (0, 0, 1) if force < 0 else (1, 0, 0)
    pipes.append(Cylinder(((line.midpoint, line.direction), radii[index]), line.length))
    pipe_properties.append({"facecolor": color})

reactions = []
reaction_properties = []
for node in network.nodes_where(is_anchor=True):
    point = network.node_point(node)
    vector = network.node_reaction(node)
    reaction = Line(point, point + vector)
    reactions.append(reaction)
    reaction_properties.append({"linecolor": (0, 1, 0), "linewidth": 10})

viewer.add(network)
viewer.add(Collection(pipes, pipe_properties))
viewer.add(Collection(reactions, reaction_properties))
viewer.show()
