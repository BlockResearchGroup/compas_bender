********************************************************************************
Installation
********************************************************************************

:mod:`compas_bender` is not released on PyPI or conda-forge yet,
so you will have to install from source.

.. code-block:: bash

    conda create -n bender python=3.9 git compas compas_occ compas_view2 --yes
    conda activate bender
    git pull https://github.com/BlockResearchGroup/compas_bender.git
    cd compas_bender
    pip install -e .
