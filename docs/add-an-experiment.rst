.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

====================
Adding an Experiment
====================

.. note: 
  TODO: If contributing an experiment, extend existing experiment.py. Otherwise create a new experiment.py in the benchmark folder for the experiments

This guide is intended for those wanting to define a new set of experiment parameters for a given benchmark. 

Similar to systems, Benchpark also provides an API where you can represent experiments 
as objects and customize their description with command line arguments.

Experiment specifications are created with ``experiment.py`` files each located in the experiment repo: ``benchpark/var/exp_repo/experiments/${Benchmark1}``. 

* If you are adding experiments to an existing benchmark, it is best to extend the current experiment.py for that benchmark in the experiment repo.

* If you are adding experiments to a benchmark you created, create a new folder for your benchmark in the experiment repo, and put your new experiment.py inside of it.

These ``experiment.py`` files inherit from the Experiment base class in ``/lib/benchpark/experiment.py`` shown below, and when used in conjunction with the system configuration files 
and package/application repositories, are used to generate a set of concrete Ramble experiments for the target system and programming model.

.. literalinclude:: ../lib/benchpark/experiment.py
   :language: python


Some or all of the functions in the Experiment base class can be overridden to define custom behavior, such as adding experiment variants. 

.. note: 
  This will change and need updates

Variants of the experiment can be added to utilize different *ProgrammingModels* used for on-node parallelization,
e.g., ``benchpark/var/exp_repo/experiments/amg2023/experiment.py`` has variant ``programming_model``, which can be 
set to ``cuda`` for an experiment using CUDA (on an NVIDIA GPU),
or ``openmp`` for an experiment using OpenMP (on a CPU).::

    class Amg2023(Experiment):
      variant(
          "programming_model",
          default="openmp",
          values=("openmp", "cuda", "rocm"),
          description="on-node parallelism model",
      )

Multiple types of experiments can be created using variants as well (e.g., strong scaling, weak scaling). See AMG2023 or Kripke for examples.

Once an experiment class has been written, an experiment is initialized with the following command, with any variants that have been defined in your experiment.py passed in as key-value pairs: 
``./bin/benchpark experiment init --dest {path/to/dest} experiment={experiment_variant} programming_model={prog_model_variant}``

For example, to run the AMG2023 strong scaling experiment for problem 1, using CUDA the command would be:
``./bin/benchpark experiment init --dest amg2023 programming_model=cuda workload=problem1 experiment=strong``

Initializing an experiment generates the following yaml files:

- ``ramble.yaml`` defines the `Ramble specs <https://googlecloudplatform.github.io/ramble/workspace_config.html#workspace-config>`_ for building, running, analyzing and archiving experiments.
- ``execution_template.tpl`` serves as a template for the final experiment script that will be concretized and executed.

A detailed description of Ramble configuration files is available at `Ramble workspace_config <https://googlecloudplatform.github.io/ramble/workspace_config.html>`_.

For more advanced usage, such as customizing hardware allocation or performance profiling see :doc:`modifiers`.


Validating the Benchmark/Experiment
-----------------------------------

To manually validate your new experiments work, you should initialize an existing system, and run your experiments. 
For example if you just created a benchmark *baz* with OpenMP and strong scaling variants it may look like this:::

  ./bin/benchpark system init --dest=genericx86-system genericx86 
  ./bin/benchpark experiment init --dest=baz-benchmark baz programming_model=openmp scaling=strong
  ./bin/benchpark setup ./baz-benchmark ./x86 workspace/


When this is complete you have successfully completed the :doc:`benchpark-setup` step and can run and analyze following the Benchpark output or following steps in :doc:`build-experiment`.

