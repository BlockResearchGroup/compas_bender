from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json
import compas_rhino

from compas_bender.datastructures import BendNetwork
from compas.utilities import geometric_key
from compas.utilities import pairwise

from compas_bender.rhino import BendNetworkArtist


HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', '..', 'data')
FILE = os.path.join(DATA, 'paper', 'arch.bender-out')

# ==============================================================================
# Network from bender-out file
# ==============================================================================

with open(FILE, 'r') as f:
    data = json.load(f)

    network = BendNetwork.from_data(data['network'])
    network.splines = data['splines']
    network.cables = data['cables']

# ==============================================================================
# Visualization
# ==============================================================================

artist = BendNetworkArtist(network, layer="BenderTest::Network::Output")
artist.clear_layer()
artist.draw_nodes(color={key: (255, 0, 0) for key in network.nodes_where({'is_anchor': True})})
artist.draw_edges()
artist.draw_axial(scale=0.01)
artist.draw_reactions(scale=0.1)
artist.redraw()
