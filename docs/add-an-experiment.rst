.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

====================
Adding an Experiment
====================

Similar to systems, Benchpark also provides an API where you can represent experiments 
as objects and customize their description with command line arguments.

Experiment specifications are created with ``experiment.py`` files 
(that inherit from the Experiment base class in ``/lib/benchpark/experiment.py``),
each located in ``benchpark/var/exp_repo/experiments/${Benchmark1}``.

Variants of the experiment can be added to utilize different *ProgrammingModels* used for on-node parallelization,
e.g., ``benchpark/var/exp_repo/experiments/amg2023/experiment.py`` has variant ``programming_model``, which can be 
set to ``cuda`` for an AMG2023 experiment using CUDA (on an NVIDIA GPU),
or ``openmp`` for an AMG2023 experiment using OpenMP (on a CPU).
These files, in conjunction with the system configuration files and package/application repositories,
are used to generate a set of concrete Ramble experiments for the target system and programming model.

An experiment is initialized with TODO: ``benchpark experiment init...``

Initializing an experiment generates the following yaml files:

- ``ramble.yaml`` defines the `Ramble specs <https://googlecloudplatform.github.io/ramble/workspace_config.html#workspace-config>`_ for building, running, analyzing and archiving experiments.
- ``execution_template.tpl`` serves as a template for the final experiment script that will be concretized and executed.

A detailed description of Ramble configuration files is available at `Ramble workspace_config <https://googlecloudplatform.github.io/ramble/workspace_config.html>`_.

Benchpark Modifiers
-------------------
In Benchpark, a ``modifier`` follows the `Ramble Modifier
<https://googlecloudplatform.github.io/ramble/tutorials/10_using_modifiers.html#modifiers>`_
and is an abstract object that can be applied to a large set of reproducible
specifications. Modifiers are intended to encasulate reusable patterns that
perform a specific configuration of an experiment. This may include injecting
performance analysis or setting up system resources.

Requesting resources with Allocation Modifier
---------------------------------------------
Given:

  - an experiment that requests resources (nodes, cpus, gpus, etc.), and
  - a specification of the resources available on the system (cores_per_node, gpus_per_node, etc.),

the ``Allocation Modifier`` generates the appropriate scheduler request for these resources
(how many nodes are required to run a given experiment, etc.).


.. list-table:: Hardware resources as specified by the system, and requested for the experiment
   :widths: 20 40 40
   :header-rows: 1

   * - Resource
     - Available on the System
     - Requested for the Experiment
   * - Total Nodes
     - (opt) sys_nodes
     - n_nodes
   * - Total MPI Ranks
     -
     - n_ranks
   * - CPU cores per node
     - sys_cores_per_node
     - (opt) n_cores_per_node
   * - GPUs per node
     - sys_gpus_per_node
     - (opt) n_gpus_per_node
   * - Memory per node
     - sys_mem_per_node
     - (opt) n_mem_per_node


The experiment is required to specify:

  - n_ranks it requires
  - n_gpus (if using GPUs)

If the experiment does not specify ``n_nodes``, the modifier will compute
the number of nodes to allocate to provide the ``n_ranks`` and/or ``n_gpus``
required for the experiment.

The system is required to specify:

  - sys_cores_per_node
  - sys_gpus_per_node (if it has GPUs)
  - sys_mem_per_node

The modifier checks the resources requested by the experiment,
computes the values for the unspecified variables, and
checks that the request does not exceed the resources available on the system.

To use the resource allocation modifier with your experiment,
add the following in your ramble.yaml::

  ramble:
    include:
      - ...
      - ./configs/modifier.yaml
    config:
      ...
    modifiers:
    - name: allocation
    applications:
      ...
    software:
      ...
    environments:
      - ...
      - '{modifier_package_name}'


Profiling with Caliper Modifier
-------------------------------
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
     - | - Min/Max/Avg time/rank: Minimum/Maximum/Average time (in seconds) across all ranks
       | - Total time: Aggregated time (in seconds) for all ranks
   * - caliper-mpi
     - Platform-independent
     - | - Same as basic caliper modifier above
       | - Profiles MPI functions
   * - caliper-topdown
     - x86 Intel CPUs
     - | - Retiring
       | - Bad speculation
       | - Front end bound
       | - Back end bound
   * - caliper-cuda
     - NVIDIA GPUs
     - | - CUDA API functions (e.g., time.gpu)

     
Validate the Experiment
------------------------

To validate the new experiment run a dryrun with a static system.

When the experiment passes the dryrun you are now ready to setup and run it, go to :doc:`4-benchpark-setup`.