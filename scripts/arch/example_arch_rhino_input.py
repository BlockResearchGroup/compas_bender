from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json
import compas_rhino

from compas_bender.datastructures import BendNetwork
from compas.utilities import geometric_key
from compas.utilities import pairwise

from compas_rhino.artists import NetworkArtist


HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "..", "data")
FILE = os.path.join(DATA, "paper", "arch.bender-in")

# ==============================================================================
# Input
# ==============================================================================

guids = compas_rhino.get_lines(layer="lines")
lines = compas_rhino.get_line_coordinates(guids)

guids = compas_rhino.get_points(layer="points")
points = compas_rhino.get_point_coordinates(guids)

guids = compas_rhino.get_polylines(layer="splines")
polylines = compas_rhino.get_polyline_coordinates(guids)

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

for polyline in polylines:
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
# Visualization
# ==============================================================================

artist = NetworkArtist(network, layer="BenderTest::Network::Input")
artist.clear_layer()
artist.draw_nodes(
    color={key: (255, 0, 0) for key in network.nodes_where({"is_anchor": True})}
)
artist.draw_edges(color={key: (0, 255, 255) for key in splines[0]["edges"]})
artist.redraw()

# ==============================================================================
# Export to bender-in
# ==============================================================================

with open(FILE, "w") as f:
    data = {"network": network.to_data(), "splines": splines, "cables": []}

    json.dump(data, f)
