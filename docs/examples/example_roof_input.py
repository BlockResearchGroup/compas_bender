from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas
import compas_rhino

from compas_bender.datastructures import BendNetwork
from compas.utilities import geometric_key
from compas.utilities import pairwise

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, "example_roof.json")

# ==============================================================================
# Input
# ==============================================================================

guids = compas_rhino.get_lines(layer="lines")
lines = compas_rhino.get_line_coordinates(guids)

guids = compas_rhino.get_points(layer="points")
points = compas_rhino.get_point_coordinates(guids)

guids = compas_rhino.get_polylines(layer="splines")
spline_polylines = compas_rhino.get_polyline_coordinates(guids)

guids = compas_rhino.get_polylines(layer="cables")
cable_polylines = compas_rhino.get_polyline_coordinates(guids)

guids = compas_rhino.get_lines(layer="ties")
tie_lines = compas_rhino.get_line_coordinates(guids)

# ==============================================================================
# Network from lines
# ==============================================================================

network = BendNetwork.from_lines(lines)

gkey_key = {
    geometric_key(network.node_attributes(node, "xyz")): node
    for node in network.nodes()
}

# ==============================================================================
# Identify anchors
# ==============================================================================

for point in points:
    gkey = geometric_key(point)
    if gkey in gkey_key:
        key = gkey_key[gkey]
        network.node_attribute(key, "is_anchor", True)

# ==============================================================================
# Identify splines
# ==============================================================================

splines = []

for polyline in spline_polylines:
    start = None
    edges = []
    for a, b in pairwise(polyline):
        a_gkey = geometric_key(a)
        b_gkey = geometric_key(b)
        if a_gkey in gkey_key and b_gkey in gkey_key:
            u = gkey_key[a_gkey]
            v = gkey_key[b_gkey]
            if start is None:
                start = u
            if network.has_edge(u, v):
                edges.append((u, v))
            else:
                edges.append((v, u))
    splines.append({"start": start, "edges": edges})

# ==============================================================================
# Identify cables
# ==============================================================================

cables = []

for polyline in cable_polylines:
    start = None
    edges = []
    for a, b in pairwise(polyline):
        a_gkey = geometric_key(a)
        b_gkey = geometric_key(b)
        if a_gkey in gkey_key and b_gkey in gkey_key:
            u = gkey_key[a_gkey]
            v = gkey_key[b_gkey]
            if start is None:
                start = u
            if network.has_edge(u, v):
                edges.append((u, v))
            else:
                edges.append((v, u))
    cables.append({"start": start, "edges": edges})

# ==============================================================================
# Identify ties
# ==============================================================================

ties = []

for a, b in tie_lines:
    a_gkey = geometric_key(a)
    b_gkey = geometric_key(b)
    if a_gkey in gkey_key and b_gkey in gkey_key:
        u = gkey_key[a_gkey]
        v = gkey_key[b_gkey]
        ties.append((u, v))

# ==============================================================================
# Export
# ==============================================================================

data = {"network": network, "splines": splines, "cables": cables, "ties": ties}

compas.json_dump(data, FILE)
