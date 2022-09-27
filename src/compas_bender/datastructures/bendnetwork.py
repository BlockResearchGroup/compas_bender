from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Line
from compas.datastructures import Network


class BendNetwork(Network):
    def __init__(self):
        super(BendNetwork, self).__init__()
        self.cables = []
        self.splines = []
        self.default_node_attributes.update(
            {
                "is_anchor": False,
                "px": 0.0,
                "py": 0.0,
                "pz": 0.0,
                "rx": 0.0,
                "ry": 0.0,
                "rz": 0.0,
                "sx": 0.0,
                "sy": 0.0,
                "sz": 0.0,
                "mx": 0.0,
                "my": 0.0,
                "mz": 0.0,
            }
        )
        self.default_edge_attributes.update(
            {
                "qpre": 1.0,
                "fpre": 0.0,
                "lpre": 0.0,
                "linit": 0.0,
                "E": 0.0,
                "radius": 0.0,
                "thickness": 0.0,
                "q": 0.0,
                "f": 0.0,
                "l": 0.0,
            }
        )

    def node_point(self, node):
        return Point(*self.node_attributes(node, "xyz"))

    def edge_line(self, edge):
        return Line(self.node_point(edge[0]), self.node_point(edge[1]))

    def node_reaction(self, node):
        if not self.node_attribute(node, "is_anchor"):
            return

        rx = self.node_attribute(node, "rx")
        ry = self.node_attribute(node, "ry")
        rz = self.node_attribute(node, "rz")
        return Vector(-rx, -ry, -rz)

    def node_residual(self, node):
        rx = self.node_attribute(node, "rx")
        ry = self.node_attribute(node, "ry")
        rz = self.node_attribute(node, "rz")
        return Vector(rx, ry, rz)
