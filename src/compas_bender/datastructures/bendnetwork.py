from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Line
from compas.datastructures import Network


class BendNetwork(Network):
    """
    Extension of the COMPAS network data structure for
    managing the relationships between the elements of a bending-active structure
    and their individual attributes.

    A BendNetwork adds the following default attributes for nodes and edges
    (there are others, but they are read-only and will be populated by the solvers):

    **nodes**

    * ``is_anchor`` : `False`
    * ``px`` : `0.0`
    * ``py`` : `0.0`
    * ``pz`` : `0.0`

    **edges**

    * ``qpre`` : `1.0`
    * ``fpre`` : `0.0`
    * ``lpre`` : `0.0`
    * ``linit`` : `0.0`
    * ``E`` : `0.0`
    * ``radius`` : `0.0`
    * ``thickness`` : `0.0`

    These attributes define the properties of the struts, ties, cablenets, and bending-active splines in the system.
    And a re then used by :func:`compas_bender.bend.bend_splines` to solve for equilibrium under the given boundary conditions.

    """

    def __init__(self, *args, **kwargs):
        super(BendNetwork, self).__init__(*args, **kwargs)
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
        """
        Return the point corresponding to the location of a node.

        Parameters
        ----------
        node : int

        Returns
        -------
        :class:`compas.geometry.Point`

        """
        return Point(*self.node_attributes(node, "xyz"))

    def edge_line(self, edge):
        """
        Return the line segment corresponding to an edge.

        Parameters
        ----------
        edge : tuple[int, int]

        Returns
        -------
        :class:`compas.geometry.Line`

        """
        return Line(self.node_point(edge[0]), self.node_point(edge[1]))

    def node_reaction(self, node):
        """
        Return the vector representing the reaction force at an anchored node.

        Parameters
        ----------
        node : int

        Returns
        -------
        :class:`compas.geometry.Vector`

        """
        if not self.node_attribute(node, "is_anchor"):
            return

        rx = self.node_attribute(node, "rx")
        ry = self.node_attribute(node, "ry")
        rz = self.node_attribute(node, "rz")
        return Vector(-rx, -ry, -rz)

    def node_residual(self, node):
        """
        Return the vector representing the residual force at a node.

        Parameters
        ----------
        node : int

        Returns
        -------
        :class:`compas.geometry.Vector`

        """
        rx = self.node_attribute(node, "rx")
        ry = self.node_attribute(node, "ry")
        rz = self.node_attribute(node, "rz")
        return Vector(rx, ry, rz)
