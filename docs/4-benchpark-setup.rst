.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

===============
Benchpark Setup
===============

Select a benchmark experiment to run, along with the programming model to use, and a system to run them on.
Also choose a directory for your experiment::

    benchpark setup benchmark/ProgrammingModel system /output/path/to/experiments_root

where:

- ``benchmark/ProgrammingModel``: amg2023/openmp | amg2023/cuda | saxpy/openmp (available choices in ``benchpark/experiments``)
- ``system``: ats2 | ats4 | cts1 (available choices in ``benchpark/configs``)

This command will assemble a Ramble workspace per experiment
with a configuration for the specified benchmark and system
with the following directory structure::

    experiments_root/
        ramble/
        spack/
        <benchmark>/
            <ProgrammingModel>/
                <system>/
                    workspace/
                        configs/
                            (everything from source/configs/<system>)
                            (everything from source/experiments/<benchmark>)

``benchpark setup`` will output instructions to follow::

   . <experiments_root>/spack/share/spack/setup-env.sh
   . <experiments_root>/ramble/share/ramble/setup-env.sh

   export SPACK_DISABLE_LOCAL_CONFIG=1

Now you are ready to compile your experiments as described in :doc:`5-build-experiment`.
