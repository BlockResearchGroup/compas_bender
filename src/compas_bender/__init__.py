"""
********************************************************************************
compas_bender
********************************************************************************

.. currentmodule:: compas_bender


.. toctree::
    :maxdepth: 1

    compas_bender.bend
    compas_bender.datastructures
    compas_bender.rhino

"""

from __future__ import print_function

import os


__author__ = ["tom van mele"]
__copyright__ = "ETH Zurich - Block Research Group"
__license__ = "MIT License"
__email__ = "tom.v.mele@gmail.com"
__version__ = "0.1.0"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
__all_plugins__ = ["compas_bender.install"]
