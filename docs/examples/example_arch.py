import os
from math import fabs
from typing import List

from compas_view2.app import App
from compas_view2.objects import Collection
from compas_view2.shapes import Arrow

import compas
from compas.colors import Color
from compas.geometry import Cylinder
from compas.geometry import Polygon
from compas.geometry import Vector
from compas.geometry import sum_vectors
from compas.utilities import remap_values
from compas_bender.bend import bend_splines
from compas_bender.datastructures import BendNetwork

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, "example_arch.json")

# ==============================================================================
# Network from file
# ==============================================================================

data = compas.json_load(FILE)

network: BendNetwork = data["network"]

splines = data["splines"]
cables = data["cables"]

for spline in splines:
    spline["edges"] = [(u, v) for u, v in spline["edges"]]

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
# Viz
# ==============================================================================

edge_index = {edge: index for index, edge in enumerate(network.edges())}
edge_index.update({(v, u): index for (u, v), index in edge_index.items()})

radii = [fabs(f) for f in network.edges_attribute("f")]
radii = remap_values(radii, 0.01, 0.2)

viewer = App()

anchors = []
anchor_properties = []
for node in network.nodes_where(is_anchor=True):
    anchors.append(network.node_point(node))
    anchor_properties.append({"pointcolor": Color.black(), "pointsize": 50})
viewer.add(Collection(anchors, anchor_properties), pointsize=20)

for node in network.nodes_where(is_anchor=True):
    point = network.node_point(node)
    nbrs = network.neighbors(node)
    edges = [(node, nbr) if network.has_edge((node, nbr)) else (nbr, node) for nbr in nbrs]
    forces = network.edges_attribute("f", keys=edges)
    edgevectors: List[Vector] = [network.node_point(nbr) - point for nbr in nbrs]
    edgevector = Vector(*sum_vectors(edgevectors))
    forcevectors = [vector.scaled(force) for force, vector in zip(forces, edgevectors)]
    forcevector = Vector(*sum_vectors(forcevectors))
    color = Color.green().darkened(50)
    vector = network.node_reaction(node)
    vector.scale(0.2)
    if vector.length > 0.1:
        if edgevector.dot(forcevector) > 0:
            position = point
        else:
            position = point - vector
        arrow = Arrow(
            position,
            vector,
            head_portion=0.2,
            head_width=0.07,
            body_width=0.02,
        )
        viewer.add(arrow, u=16, facecolor=color)

for spline in splines:
    pipes = []
    pipe_properties = []
    for u, v in spline["edges"]:
        edge = (u, v) if network.has_edge((u, v)) else (v, u)
        index = edge_index[edge]
        # bending moment
        ma = Vector(*network.node_attributes(u, ["mx", "my", "mz"]))
        mb = Vector(*network.node_attributes(v, ["mx", "my", "mz"]))
        a = network.node_point(u)
        b = network.node_point(v)
        aa = a + ma * 0.03
        bb = b + mb * 0.03
        viewer.add(Polygon([a, b, bb, aa]), facecolor=(1, 1, 0))
        # axial force
        force = network.edge_attribute(edge, "f")
        line = network.edge_line((u, v))
        radius = radii[index]
        color = Color.red() if force > 0 else Color.blue()
        pipe = Cylinder.from_line_and_radius(line, radius)
        pipes.append(pipe)
        pipe_properties.append({"facecolor": color})
    viewer.add(Collection(pipes, pipe_properties))

for cable in cables:
    pipes = []
    pipe_properties = []
    for edge in cable["edges"]:
        index = edge_index[edge]
        force = network.edge_attribute(edge, "f")
        line = network.edge_line((u, v))
        radius = radii[index]
        color = Color.red() if force > 0 else Color.blue()
        pipe = Cylinder.from_line_and_radius(line, radius)
        pipes.append(pipe)
        pipe_properties.append({"facecolor": color})
    viewer.add(Collection(pipes, pipe_properties))

viewer.add(network, show_points=False, linewidth=2)
viewer.show()
