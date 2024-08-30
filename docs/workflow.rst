.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==============================
The Benchpark Workflow
==============================

A benchpark workflow consists of the following steps:

1. Initialize the system: build the correct system configuration files (i.e. for the hardware you want to run on)
2. Initialize the experiments: build the experiment configuration files
3. Setup the experiments: validate that the experiment and system configurations are compatible, create ramble input files and experiment root directory
4. Build the experiments: build the source code, and setup the experiment directory structure within the root directory (can this be combined with prev step?)
5. Run the experiments: run the code built in the previous step, output files are stored in proper directory structure
6. Analyze the experiments: ramble generates a summary of results

Once you have cloned the repository and installed it (Getting Started page) you can either run an existing configuration as is, or create a new one for your system by following the steps below.

1. ** Initialize the System **

To run benchpark on a system that does not have an existing configuration in var/sys_repo already, it is recommended to either start with one of the existing configurations that is similar, or start with a generic example (e.g., generic_x86).

We provide an example of editing the generic_x86 system configurations. 

The main driver for configuring a system is done by defining a subclass for that system in a var/sys_repo/<System>/system.py file, which inherits from the System base class defined in /lib/benchpark/system.py.

As is, the x86_64 system subclass should work for most x86_64 systems, but potential common changes might be to edit the number of cores per cpu, compiler locations, or adding external packages.

TODO: Examples of making these changes...

Once the system subclass is written with proper configurations run: 
``./benchpark system init --dest </path/to/destination/folder> x86_64``

This will generate the required yaml configurations for your system and you can move on to experiments.

2. ** Initialize the Experiments **

Similar to systems, all experiments are configured by an Experiment subclass that inherits from the Experiment base class in /lib/benchpark/experiment.py.

To initialize the saxpy experiments for a cpu only system you would run:

To update it for a gpu system...

3. ** Setup the experiments **

Once the experiments you want to run have been initialized you can run setup, this will validate that the system and experiment are compatible and create a root directory for your experiments.

``benchpark setup <Benchmark/ProgrammingModel> <System> </output/path/to/experiments_root>``

4. ** Build the Experiments **

Now that the experiments are validated, ramble will build the source code for the experiments and further setup the directory structure for each experiment:

``ramble -P -D . workspace setup``

5. ** Run the Experiments **

To run all of the experiments in a workspace:

``ramble -P -D . on``

6. ** Analyze the Experiments ** 

Ramble will automatically analyze and create a summary of experiment results in a workspace.

``ramble -P -D . workspace analyze``





