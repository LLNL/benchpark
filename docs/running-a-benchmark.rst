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

``cd $workspace``

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

To simplify the configuration process, we provide a script with the Benchpark repository ``$benchpark/bin/benchpark``

This script 

Create a directory for a given experiment
----------------------------------------- 
```
cd ${APP_WORKING_DIR}/workspace 
```
Set up a workspace
-----------------------------------------
```
ramble -D . workspace setup 
```

Run the experiment
-----------------------------------------
```
ramble -D . on 
```

Analyze the experiment results 
-----------------------------------------
```
ramble -D . workspace analyze 
```
