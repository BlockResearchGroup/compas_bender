from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import compas_rhino
import compas_rhino.objects

import compas
from compas.itertools import pairwise
from compas.tolerance import TOL
from compas_bender.datastructures import BendNetwork

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, "example_arch.json")

# ==============================================================================
# Input
# ==============================================================================

guids = compas_rhino.objects.get_lines(layer="lines")
lines = compas_rhino.objects.get_line_coordinates(guids)

guids = compas_rhino.objects.get_points(layer="points")
points = compas_rhino.objects.get_point_coordinates(guids)

guids = compas_rhino.objects.get_polylines(layer="splines")
polylines = compas_rhino.objects.get_polyline_coordinates(guids)

# ==============================================================================
# Network from lines
# ==============================================================================

network = BendNetwork.from_lines(lines)

gkey_key = {TOL.geometric_key(network.node_attributes(node, "xyz")): node for node in network.nodes()}

# ==============================================================================
# Identify anchors
# ==============================================================================

for point in points:
    gkey = TOL.geometric_key(point)
    if gkey in gkey_key:
        key = gkey_key[gkey]
        network.node_attribute(key, "is_anchor", True)

# ==============================================================================
# Identify splines
# ==============================================================================

splines = []

for polyline in polylines:
    start = None
    edges = []
    for a, b in pairwise(polyline):
        a_gkey = TOL.geometric_key(a)
        b_gkey = TOL.geometric_key(b)
        if a_gkey in gkey_key and b_gkey in gkey_key:
            u = gkey_key[a_gkey]
            v = gkey_key[b_gkey]
            if start is None:
                start = u
            if network.has_edge((u, v)):
                edges.append((u, v))
            else:
                edges.append((v, u))
    splines.append({"start": start, "edges": edges})

# ==============================================================================
# Export
# ==============================================================================

data = {"network": network, "splines": splines, "cables": []}

compas.json_dump(data, FILE)
