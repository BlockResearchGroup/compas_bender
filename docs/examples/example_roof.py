import os
from math import fabs

from compas_viewer import Viewer

import compas
from compas.colors import Color
from compas.geometry import Cylinder
from compas.geometry import Line
from compas.geometry import Polygon
from compas.geometry import Vector
from compas.geometry import sum_vectors
from compas.itertools import remap_values
from compas_bender.bend import bend_splines
from compas_bender.datastructures import BendNetwork

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, "example_roof.json")

# ==============================================================================
# Network from file
# ==============================================================================

data = compas.json_load(FILE)

network: BendNetwork = data["network"]

splines = data["splines"]
cables = data["cables"]
ties = data["ties"]

for spline in splines:
    spline["edges"] = [(u, v) for u, v in spline["edges"]]

for cable in cables:
    cable["edges"] = [(u, v) for u, v in cable["edges"]]
    cable["qpre"] = 7

ties = [(u, v) if network.has_edge((u, v)) else (v, u) for u, v in ties]

# ==============================================================================
# Spline parameters
# ==============================================================================

for spline in splines:
    spline["E"] = 30
    spline["radius"] = 20
    spline["thickness"] = 5

for key, attr in network.edges(True):
    attr["linit"] = 0

# ==============================================================================
# Ties
# ==============================================================================

for edge in ties:
    line = network.edge_line(edge)
    network.edge_attribute(edge, "lpre", 0.97 * line.length)

# ==============================================================================
# Bend
# ==============================================================================

bend_splines(
    network,
    cables,
    splines,
    config={"kmax": 10000, "tol1": 1e-3, "tol2": 1e-2, "tol3": 1e-4, "alpha": 100},
)

# ==============================================================================
# Viz
# ==============================================================================


edge_index = {edge: index for index, edge in enumerate(network.edges())}
edge_index.update({(v, u): index for (u, v), index in edge_index.items()})

radii = [fabs(f) for f in network.edges_attribute("f")]
radii = remap_values(radii, 0.01, 0.2)

viewer = Viewer()

anchors = []
for node in network.nodes_where(is_anchor=True):
    anchors.append(network.node_point(node))
viewer.scene.add(anchors, pointsize=20)

reactions = []
for node in network.nodes_where(is_anchor=True):
    point = network.node_point(node)
    nbrs = network.neighbors(node)
    edges = [(node, nbr) if network.has_edge((node, nbr)) else (nbr, node) for nbr in nbrs]
    forces = network.edges_attribute("f", keys=edges)
    edgevectors: list[Vector] = [network.node_point(nbr) - point for nbr in nbrs]
    edgevector = Vector(*sum_vectors(edgevectors))
    forcevectors = [vector.scaled(force) for force, vector in zip(forces, edgevectors)]
    forcevector = Vector(*sum_vectors(forcevectors))
    color = Color.green().darkened(50)
    vector = network.node_reaction(node)
    vector.scale(0.2)
    if edgevector.dot(forcevector) > 0:
        position = point
    else:
        position = point - vector
    line = Line.from_point_and_vector(position, vector)
    reactions.append((line, {"linecolor": color, "linewidth": 3}))
viewer.scene.add(reactions)

for spline in splines:
    pipes = []
    polygons = []

    for u, v in spline["edges"]:
        edge = (u, v) if network.has_edge((u, v)) else (v, u)
        index = edge_index[edge]
        # bending moment
        ma = Vector(*network.node_attributes(u, ["mx", "my", "mz"]))
        mb = Vector(*network.node_attributes(v, ["mx", "my", "mz"]))
        if ma and mb:
            a = network.node_point(u)
            b = network.node_point(v)
            aa = a + ma * 0.005
            bb = b + mb * 0.005
            polygons.append((Polygon([a, b, bb, aa]), {"color": Color.yellow()}))
        # axial force
        force = network.edge_attribute(edge, "f")
        line = network.edge_line((u, v))
        radius = radii[index] * 0.5
        color = Color.red() if force > 0 else Color.blue()
        pipe = Cylinder.from_line_and_radius(line, radius)
        pipes.append((pipe, {"color": color}))
    viewer.scene.add(pipes)
    viewer.scene.add(polygons)

for cable in cables:
    pipes = []
    for edge in cable["edges"]:
        index = edge_index[edge]
        force = network.edge_attribute(edge, "f")
        line = network.edge_line((u, v))
        radius = radii[index]
        color = Color.red() if force > 0 else Color.blue()
        pipe = Cylinder.from_line_and_radius(line, radius)
        pipes.append((pipe, {"color": color}))
    viewer.scene.add(pipes)

pipes = []
for edge in ties:
    index = edge_index[edge]
    force = network.edge_attribute(edge, "f")
    line = network.edge_line(edge)
    radius = radii[index]
    color = Color.red() if force > 0 else Color.blue()
    pipe = Cylinder.from_line_and_radius(line, radius)
    pipes.append((pipe, {"color": color}))
viewer.scene.add(pipes)

viewer.scene.add(network, show_points=False, linewidth=2)
viewer.show()
