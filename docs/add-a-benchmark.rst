.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==================
Adding a Benchmark
==================

The following system-independent specification is required for each ${Benchmark1}:

- ``package.py`` is a Spack specification that defines how to build and install ${Benchmark1}.
- ``application.py`` is a Ramble specification that defines the ${Benchmark1} input and parameters.

During ``benchpark setup`` the user selects ${Benchmark1} to run as the following::

     benchpark setup ${Benchmark1}/${ProgrammingModel1} ${System1} </output/path/to/experiments_root>

By default, Benchpark will use ${Benchmark1} specifications (``package.py`` and ``application.py``)
provided in the Spack and Ramble repos.
It is possible to overwrite the benchmark specifications provided in the Spack and Ramble repos;
see :doc:`FAQ-benchpark-repo` for details.
