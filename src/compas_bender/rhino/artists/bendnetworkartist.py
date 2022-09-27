from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import math
import compas_rhino

from compas.geometry import scale_vector
from compas.geometry import length_vector
from compas.geometry import add_vectors

from compas_rhino.artists import NetworkArtist


class BendNetworkArtist(NetworkArtist):
    def draw_axial(self, scale=1.0, tol=1e-3):
        """Draw axial forces as cylinders around the corresponding edges.

        Parameters
        ----------
        scale : float, optional
            Scale for the cylinder radius.
            Default is ``1.0``.
        tol : float, optional
            Cylinders with a radius (after scaling)
            smaller than this tolerance will not be drawn.
            Default is ``1e-3``.

        Returns
        -------
        list of guid
            The identifiers of the objects that were added to the Rhino model space.
        """
        fabs = math.fabs
        cylinders = []
        for edge, attr in self.network.edges(True):
            force = attr["f"]
            if force > 0:
                color = (255, 0, 0)
            elif force < 0:
                color = (0, 0, 255)
            else:
                continue
            radius = 0.5 * fabs(force) * scale
            if radius < tol:
                continue
            start, end = self.network.edge_coordinates(*edge)
            cylinders.append(
                {"start": start, "end": end, "radius": radius, "color": color}
            )
        return compas_rhino.draw_cylinders(
            cylinders, layer=self.layer, clear=False, redraw=False
        )

    def draw_reactions(self, scale=1.0, tol=1e-3):
        """Draw reaction forces as force vectors at the anchored nodes.

        Parameters
        ----------
        scale : float, optional
            Scale for the length of the vectors.
            Default is ``1.0``.
        tol : float, optional
            Vectors with a length (after scaling)
            smaller than this tolerance will not be drawn.
            Default is ``1e-3``.

        Returns
        -------
        list of guid
            The identifiers of the objects that were added to the Rhino model space.
        """
        lines = []
        for node, attr in self.network.nodes_where({"is_anchor": True}, True):
            start = self.network.node_coordinates(node)
            vector = [attr["rx"], attr["ry"], attr["rz"]]
            length = length_vector(vector)
            if length * scale < tol:
                continue
            end = add_vectors(start, scale_vector(vector, scale))
            lines.append(
                {"start": start, "end": end, "arrow": "end", "color": (0, 255, 0)}
            )
        return compas_rhino.draw_lines(
            lines, layer=self.layer, clear=False, redraw=False
        )

    # def draw_shear(self, scale=1.0, tol=1e-3):
    #     """Draw shear forces at nodes of the splines.

    #     Parameters
    #     ----------
    #     scale : float, optional
    #         Scale for the shear forces.
    #         Default is ``1.0``.
    #     tol : float, optional
    #         Shear forces with a length (after scaling)
    #         smaller than this tolerance will not be drawn.
    #         Default is ``1e-3``.

    #     Returns
    #     -------
    #     list of guid
    #         The identifiers of the objects that were added to the Rhino model space.
    #     """
    #     for spline in self.network.splines:


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
