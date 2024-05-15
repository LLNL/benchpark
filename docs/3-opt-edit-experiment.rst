.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==========================
(optional) Edit experiment
==========================

Benchpark configuration files are organized as follows::

  $benchpark
  ├── configs
  │  ├── ${SYSTEM1}
  │  │  ├── auxiliary_software_files
  │  │  │  ├── compilers.yaml
  │  │  │  └── packages.yaml
  │  │  ├── spack.yaml
  │  │  └── variables.yaml
  ├── experiments
  │  ├── ${BENCHMARK1}
  │  │  ├── ${ProgrammingModel1}
  │  │  │  ├── execute_experiment.tpl
  │  │  │  └── ramble.yaml
  │  │  ├── ${ProgrammingModel1}
  │  │  │  ├── execute_experiment.tpl
  │  │  │  └── ramble.yaml
  └── repo
     ├── ${BENCHMARK1}
     │  ├── application.py
     │  └── package.py
     └── repo.yaml

You can edit these configuration files to change the behavior of your experiments.

System specification
--------------------
Files under ``benchpark/configs/${SYSTEM}`` provide the specification
of the software stack on your system
(see :doc:`add-a-system-config` for details).

Experiment specification
------------------------
Files under ``benchpark/experiments/${BENCHMARK}/${ProgrammingModel}``
provide the specifications for the experiments.
If you would like to make changes to your experiments,  such as enabling
specific tools to measure the performance of your experiments,
you can manually edit the specifications in ``ramble.yaml``
(see :doc:`add-an-experiment` for details).

Benchmark specification
-----------------------
If you would like to modify a specification of your benchmark,
you can do so by upstreaming changes to Spack and/or Ramble,
or working on your benchmark specification in ``benchpark/repo/${BENCHMARK}``
(see :doc:`add-a-benchmark` for details).

Modifiers
---------
In Benchpark, a ``modifier`` follows the `Ramble Modifier
<https://googlecloudplatform.github.io/ramble/tutorials/10_using_modifiers.html#modifiers>`_
and is an abstract object that can be applied to a large set of reproducible
specifications. Modifiers are intended to encasulate reusable patterns that
perform a specific configuration of an experiment. This may include injecting
performance analysis or setting up system resources.

Applying the Caliper modifier
-----------------------------
We have implemented a Caliper modifier to enable profiling of Caliper-instrumented
benchmarks in Benchpark. More documentation on Caliper can be found `here
<https://software.llnl.gov/Caliper>`_.

To turn on profiling with Caliper, add ``--modifier=<caliper_modifier>`` to the Benchpark
setup step::

    ./benchpark setup <Benchmark/ProgrammingModel> <System> --modifier=<caliper_modifier> <workspace-dir>

Valid values for ``<caliper_modifier>`` are found in the **Caliper Modifier**
column of the table below.  Benchpark will link the experiment to Caliper,
and inject appropriate Caliper configuration at runtime.  After the experiments
in the workspace have completed running, a ``.cali`` file
is created which contains the collected performance metrics.

.. list-table:: Available caliper modifiers
   :widths: 20 20 50
   :header-rows: 1

   * - Caliper Modifier
     - Where Applicable
     - Metrics Collected
   * - caliper
     - Platform-independent
     - | - Min time/rank: Minimum time (in seconds) across all ranks
       | - Max time/rank: Maximum time (in seconds) across all ranks
       | - Avg time/rank: Average time (in seconds) across all ranks
       | - Total time: Aggregated time (in seconds) over all ranks
   * - caliper-topdown
     - x86 Intel CPUs
     - | - Retiring
       | - Bad speculation
       | - Front end bound
       | - Back end bound
   * - caliper-cuda
     - NVIDIA GPUs
     - | - CUDA API functions (e.g., time.gpu)
