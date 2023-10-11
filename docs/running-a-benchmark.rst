=================================
Running a benchmark in Benchpark
=================================
After installing Benchpark, select a benchmark experiment to run on a specified system type.

Benchpark experiments are modeled as a `Ramble workspace <https://googlecloudplatform.github.io/ramble/workspace.html>`_ – a set of self-contained configuration files required to correctly build and execute those experiments.

Understanding Benchpark repository structure
-----------------------------------------

The structure of the benchpark repository is as follows:

```
$benchpark
| ├── configs
| │  ├── ats4
| │  │  ├── auxiliary_software_files
| │  │  │  ├── compilers.yaml
| │  │  │  └── packages.yaml
| │  │  ├── spack.yaml
| │  │  └── variables.yaml
| │  ├── cts1
| │  │  ├── auxiliary_software_files
| │  │  │  ├── compilers.yaml
| │  │  │  └── packages.yaml
| │  │  ├── spack.yaml
| │  │  └── variables.yaml
| ├── experiments
| │  ├── amg2023
| │  │  ├── cuda
| │  │  │  ├── execute_experiment.tpl
| │  │  │  └── ramble.yaml
| │  │  ├── openmp
| │  │  │  ├── execute_experiment.tpl
| │  │  │  └── ramble.yaml
| │  ├── saxpy
| │  │  ├── cuda
| │  │  │  ├── execute_experiment.tpl
| │  │  │  └── ramble.yaml
| │  │  ├── openmp
| │  │  │  ├── execute_experiment.tpl
| │  │  │  └── ramble.yaml
| └── repo
|     ├── amg2023
|     │  ├── application.py
|     │  └── package.py
|     ├── hypre
|     │  └── package.py
|     ├── saxpy
|     │  ├── application.py
|     │  └── package.py
|     └── repo.yaml
```

In order to create a concrete set of experiments for a benchmark on a given target system, we require the following three sets of config files:

**System-specific** – These specs are located in ``$benchpark/configs``. These are Spack configuration files required to build the code on a given system e.g. ``ats4`` or ``cts1``. The user can either use an existing system configuration provided by benchpark for instance, ``$benchpark/configs/ats4`` or provide their own configuration at ``$benchpark/configs``. For a target system, files ``compilers.yaml`` and ``packages.yaml`` `provide <https://spack.readthedocs.io/en/latest/configuration.html>`_, respectively, the compilers and package definitions (e.g. MPI) required by Spack to build an application on that system. ``spack.yaml`` provides names for Spack compiler/packages specs that are used by Ramble to create its Spack environment. ``variables.yaml`` defines system-specific variables to be used by the experiments e.g. application launcher and job scheduler available on the system.

**Application-specific** – These specs are located in ``$benchpark/repo``. These are system-independent specifications for building and running an application. Spack needs a `package repository <https://spack.readthedocs.io/en/latest/repositories.html>`_ with `instructions  <https://spack-tutorial.readthedocs.io/en/latest/tutorial_packaging.html#creating-the-package-file>`_ to build and install an application and each of its dependent packages (e.g. ``$benchpark/repo/amg2023/package.py`` and ``$benchpark/repo/hypre/package.py``.) Similarly, Ramble needs an application repository that defines the benchmark input and run specification (e.g. $benchpark/repo/amg2023/application.py.) An application can either use the built-in repositories shipped with the default Spack/Ramble repos or define a new repository in ``$benchpark/repo``. For a custom repository, Spack and Ramble must be pointed to the location of the correct spec files as follows:

``spack repo add --scope=site $benchpark/repo
ramble repo add --scope=site $benchpark/repo``

The top-level ``repo.yaml`` provides a unique namespace for the benchpark repository.

**Experiment-specific** – These specs are located in ``$benchpark/experiments``. They are organized by the target "backend" for the experiment e.g. ``$benchpark/experiment/amg2023/cuda`` for a CUDA-based experiment and ``$benchpark/experiment/amg2023/openmp`` for an OpenMP-based experiment. These files, in conjunction with the system configuration files and package/application repositories, are used to generate a set of concrete Ramble experiments for the target system and backend. ``ramble.yaml`` defines the `Ramble specs <https://googlecloudplatform.github.io/ramble/workspace_config.html#workspace-config>`_ for building, running, analyzing and archiving experiments. ``execution_template.tpl`` provides the template script from which the final experiment script to be executed is concretized.

Configuring Benchpark experiments
-----------------------------------------
The following steps should be followed to configure an experiment in Benchpark:

1. Clone the Benchpark repository at some location ``$benchpark``

``git clone git@github.com:LLNL/benchpark.git $benchpark``

2. Add the required system-, application- and experiment-specific config files for the benchmark to ``$benchpark`` as desribed `above <https://github.com/LLNL/benchpark/edit/rfhaque-patch-1/docs/running-a-benchmark.rst?pr=%2FLLNL%2Fbenchpark%2Fpull%2F19#understanding-benchpark-repository-structure>`_

3. Create an experiment directory at some location ``$workspace``

``mkdir $workspace``

4. Clone the Spack and Ramble repositories. Skip this step if Spack/Ramble installation is already available

``git clone --depth=1 -c feature.manyFiles=true https://github.com/spack/spack.git $workspace/spack``

``git clone --depth=1 -c feature.manyFiles=true https://github.com/GoogleCloudPlatform/ramble.git $workspace/ramble``

5. Source the Spack/Ramble shell scripts for your environment

``. $workspace/spack/share/spack/setup-env.sh``

``. $workspace/ramble/share/ramble/setup-env.sh``

6. Clean the spack and Ramble environment

``export SPACK_DISABLE_LOCAL_CONFIG=1``

``rm -rf ~/.ramble/repos.yaml``

7. Point Spack and Ramble to the Benchpark package and application repository

``spack repo add --scope=site $benchpark/repo``

``ramble repo add --scope=site $benchpark/repo``

8. Copy the required system and experiment config files to $workspace

``cp -r $benchpark/configs/ats4/* $workspace/configs``

``cp -r $benchpark/experiments/amg2023/cuda/* $workspace/configs``

To simplify the configuration process, we provide a script with the Benchpark repository ``$benchpark/bin/benchpark``

This script takes as input the system name, experiment backend name and the location of the experiment directory and sets the Spack/Ramble configuration appropriately.

``$benchpark/bin/benchpark amg2023/cuda ats4 $workspace``

Building the benchmark and setting up a workspace
----------------------------------------- 
This step builds the application using Spack.

``cd $workspace``

``ramble -D . workspace setup``

It also creates the set of concrete experiments to be executed. After workspace setup is complete, Ramble creates a ``$workspace/experiments`` directory with a unique subdirectory for each experiment instance

```
$workspace
| └── experiments
|    └── amg2023
|        └── problem1
|            ├── amg2023_cuda11.8.0_problem1_1_8_2_2_2_10_10_10
|            │   ├── execute_experiment
|            │   └── ...
|            ├── amg2023_cuda11.8.0_problem1_2_4_2_2_2_10_10_10
|            │   ├── execute_experiment
|            │   └── ...
|            ├── amg2023_cuda11.8.0_problem1_1_8_2_2_2_20_20_20
|            │   ├── execute_experiment
|            │   └── ...
|            └── amg2023_cuda11.8.0_problem1_2_4_2_2_2_20_20_20
|                ├── execute_experiment
|                └── ...
```
Each instance gets its own ``execute_experiment`` script that is used to set input paramaters/environment variables, run the experiment and generate the output.

Run the experiment(s)
-----------------------------------------
This step runs all the experiments in the workspace. An output file is generated for each experiment in its unique directory.

``ramble -D . on``

```
$workspace
| └── experiments
|    └── amg2023
|        └── problem1
|            ├── amg2023_cuda11.8.0_problem1_1_8_2_2_2_10_10_10
|            │   ├── execute_experiment
|            │   ├── amg2023_cuda11.8.0_problem1_1_8_2_2_2_10_10_10.out
|            │   └── ...
|            ├── amg2023_cuda11.8.0_problem1_2_4_2_2_2_10_10_10
|            │   ├── execute_experiment
|            │   ├── amg2023_cuda11.8.0_problem1_2_4_2_2_2_10_10_10.out
|            │   └── ...
|            ├── amg2023_cuda11.8.0_problem1_1_8_2_2_2_20_20_20
|            │   ├── execute_experiment
|            │   ├── amg2023_cuda11.8.0_problem1_1_8_2_2_2_20_20_20.out
|            │   └── ...
|            └── amg2023_cuda11.8.0_problem1_2_4_2_2_2_20_20_20
|                ├── execute_experiment
|                ├── amg2023_cuda11.8.0_problem1_2_4_2_2_2_20_20_20.out
|                └── ...
```

An experiment instance can also be executed individually by directly invoking its ``execute_experiment`` script (e.g. ``$workspace/experiments/amg2023/problem1/amg2023_cuda11.8.0_problem1_1_8_2_2_2_10_10_10/execute_experiment``)
Note that rerunning experiments overwrites any existing output files.

Analyze the experiment results 
-----------------------------------------
Once the experiments have been run, the command 

```
ramble -D . workspace analyze 
```

is used to analyze figures of merit and evaluate `success/failure <https://googlecloudplatform.github.io/ramble/success_criteria.html>`_ of the experiments. Ramble generates a summary results file at ``$workspace``

