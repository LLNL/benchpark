.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

================
Build experiment
================

``benchpark setup`` has set up the directory structure for your experiment.
The next step is setting up the Ramble workspace and building the code::

   cd <experiments_root>/<benchmark/ProgrammingModel>/<system>/workspace
   ramble -P -D . workspace setup


Ramble will build the source code and set up the following workspace directory structure::

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
                        experiments/
                            <benchmark>/
                                <problem>/
                                    <benchmark>_<ProgrammingModel>_<problem>
                                        execute_experiment

If you edit any of the files, see :doc:`FAQ-what-to-rerun` to determine
whether you need to re-do any of the previous steps.
