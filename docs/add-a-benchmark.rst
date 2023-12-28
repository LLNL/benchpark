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

benchpark/repo
--------------
If  you are working on a benchmark that is not (yet) available in Spack and/or Ramble,
or you would like to override the benchmark specifications available in Spack and/or Ramble,
you can add the following specification in the ``benchpark/repo``::

  benchpark
  └── repo 
     ├── ${BENCHMARK1} 
     │  ├── application.py 
     │  └── package.py 
     └── repo.yaml 

where ``application.py`` is a Ramble specification for the benchmark,
``package.py`` is a Spack specification for the benchmark, and
``repo.yaml`` points at those two files, indicating to Benchpark
to use them instead of the specifications that may be available in Spack and/or Ramble repos.
