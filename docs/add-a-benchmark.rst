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

==============
benchpark/repo
==============
It is possible to overwrite the benchmark specifications provided in the Spack and Ramble repos.
To do so, add ``package.py`` and/or ``application.py`` for ${Benchmark1} in 
``benchpark/repo/${Benchmark1}``::

  benchpark
  └── repo
     ├── ${Benchmark1}
     │  ├── application.py
     │  └── package.py
     └── repo.yaml

``benchpark/repo`` can be used as a staging area for the build and run specification for 
${Benchmark1} so that you can test them together with your experiment specification 
on a given system.  Once the experiment is working and merged into the develop branch of Benchpark,
we would like to encourage the contributors to upstream the ``package.py`` to Spack,
and the ``application.py`` to Ramble.  When those PRs are approved and merged,
please submit a PR to remove the duplicated specification from ``benchpark/repo``.
