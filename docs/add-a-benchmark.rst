.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==================
Adding a Benchmark
==================

The following system-independent specification is required for each benchmark:

- ``package.py`` is a Spack specification that defines how to build and install the benchmark.
- ``application.py`` is a Ramble specification that defines the benchmark input and parameters.

By default, Benchpark will use the benchmark specifications provided in the Spack and Ramble repos.

==============
benchpark/repo
==============
Benchpark provides a staging area for the build and run specification for a benchmark
so that you can test them together with your experiment specification on a given system::

  benchpark
  └── repo
     ├── ${BENCHMARK1}
     │  ├── application.py
     │  └── package.py
     └── repo.yaml

where ``application.py`` is a Ramble specification for the benchmark,
``package.py`` is a Spack specification for the benchmark.

Benchpark will use this benchmark specification in its experiments.
If the specification also exists in Spack and/or Ramble,
the specification in ``benchpark/repo`` will overwrite it.
