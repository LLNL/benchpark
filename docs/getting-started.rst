===============
Getting Started
===============

Python 3.6 and git are required to install Benchpark::

  $ git clone https://github.com/llnl/benchpark.git
  $ cd benchpark/bin
  $ ./benchpark benchmark/ProgrammingModel system /output/path/to/workspace

where:

- ``benchmark/ProgrammingModel``: amg2023/openmp | amg2023/cuda | saxpy/openmp (available choices in benchpark/experiments)
- ``system``: ats2 | ats4 | cts1 (available choices in benchpark/configs)

