********************************************************************************
Installation
********************************************************************************

Stable
======

Not available yet...


Development
===========

To install `compas_assembly` for development, install from local source with the "dev" requirements.

.. code-block:: bash

    conda create -n bender python=3.9 git compas compas_occ --yes
    conda activate bender
    git pull https://github.com/blockresearchgroup/compas_bender.git
    cd compas_bender
    pip install -e ".[dev]"
