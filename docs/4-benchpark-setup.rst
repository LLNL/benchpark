.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

====================
Setting up Benchpark
====================

Select a benchmark experiment to run, along with the programming model to use, and a system to run them on.
Also choose a directory for your experiment::

    benchpark setup <Benchmark/ProgrammingModel> <System> </output/path/to/experiments_root>

where:

- ``<Benchmark/ProgrammingModel>``: amg2023/openmp | amg2023/cuda | saxpy/openmp (available choices in ``benchpark/experiments``)
- ``<System>``: nosite-x86_64 | LLNL-Sierra-IBM-power9-V100-Infiniband | RCCS-Fugaku-Fujitsu-A64FX-TofuD | nosite-AWS_PCluster_Hpc7a-zen4-EFA (available choices in :doc:`available-system-specs`)

This command will assemble a Ramble workspace per experiment
with a configuration for the specified benchmark and system
with the following directory structure::

    experiments_root/
        ramble/
        spack/
        <Benchmark/ProgrammingModel>/
            <System>/
                workspace/
                    configs/
                        (everything from source/configs/<System>)
                        (everything from source/experiments/<Benchmark/ProgrammingModel>)

``benchpark setup`` will output instructions to follow::

   . <experiments_root>/setup.sh

The ``setup.sh`` script calls the Spack and Ramble setup scripts.  It optionally accepts
parameters to ``ramble workspace setup`` as `documented in Ramble
<https://googlecloudplatform.github.io/ramble/workspace.html#setting-up-a-workspace>`_,
including ``--dry-run`` and ``--phases make_experiments``.

Now you are ready to compile your experiments as described in :doc:`5-build-experiment`.
