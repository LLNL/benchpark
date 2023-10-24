==================
Adding a Benchmark
==================

**Benchmark specification:** Specifications for building and running a specific application/benchmark, independent of the target system. The following is required for each ``${BENCHMARK}``: 

- ``package.py`` is a Spack specification that defines how to build and install the benchmark.
- ``application.py`` is a Ramble specification that defines the benchmark input and parameters.

By default, upstreamed benchmark specifications provided in the Spack and Ramble repos will be used.

benchpark/repo
--------------
If  you are working on a benchmark that is not upstreamead to Spack and/or Ramble,
you may introduce the following code::

  $benchpark
  └── repo 
     ├── ${BENCHMARK1} 
     │  ├── application.py 
     │  └── package.py 
     └── repo.yaml 

where ``application.py`` is a Ramble specification for the benchmark,
``package.py`` is a Spack specification for the benchmark, and
``repo.yaml`` points at those two files.

The user can override the benchmark specifications upstreamed to Spack and/or Ramble
by providing custom specifications in ``$benchpark/repo``, 
and pointing Spack and Ramble to these custom specifications instead::

  spack repo add --scope=site ${APP_SOURCE_DIR}/repo 
  ramble repo add --scope=site ${APP_SOURCE_DIR}/repo 

Note that the ``${APP_SOURCE_DIR}/repo`` needs a ``repo.yaml`` to distinguish the application’s spec 
from the default Spack and/or Ramble spec for the same application, if one exists. 
