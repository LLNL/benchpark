===================
Benchpark 
===================
To list all available benchmarks and systems::

  benchpark list
 
Configuration files are organized as follows:: 

  $benchpark 
  ├── bin
  │  ├── benchpark
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


A complete experiment specification requires three types of config files:  

1. **System specification:** Configuration files required by Spack to build the code on the target system, and for Ramble to run on the target system, are located in ``$benchpark/configs``. The following is required for each given system ``${SYSTEM}``:

- ``compilers.yaml`` define the compilers on the system.
- ``packages.yaml`` define the pre-installed packages  (e.g., system MPI) on the system.
- ``spack.yaml`` defines names for Spack compiler and package specs. 
- ``variables.yaml`` defines system-specific launcher and job scheduler. 
 
2. **Benchmark specification:** Specifications for building and running a specific application/benchmark, independent of the target system. The following is required for each ``${BENCHMARK}``: 

- ``package.py`` is a Spack specification that defines how to build and install the benchmark.
- ``application.py`` is a Ramble specification that defines the benchmark input and parameters.

By default, upstreamed benchmark specifications provided in the Spack and Ramble repos will be used.
The user can override these default benchmark specifications by providing custom specifications in ``$benchpark/repo``, 
and pointing Spack and Ramble to these custom specifications instead::
  spack repo add --scope=site ${APP_SOURCE_DIR}/repo 
  ramble repo add --scope=site ${APP_SOURCE_DIR}/repo 

Note that the ``${APP_SOURCE_DIR}/repo`` needs a ``repo.yaml`` to distinguish the application’s spec 
from the default Spack and/or Ramble spec for the same application, if one exists. 


3. **Experiment specification:** Experiment specifications are located in ``$benchpark/experiments``. 
They are organized by the *ProgrammingModel* used for on-node parallelization for the experiment, 
e.g., ``$benchpark/experiments/amg2023/cuda`` for an AMG2023 experiment using CUDA (on an NVIDIA GPU),
and ``$benchpark/experiments/amg2023/openmp`` for an AMG2023 experiment using OpenMP (on a CPU). 
These files, in conjunction with the system configuration files and package/application repositories, 
are used to generate a set of concrete Ramble experiments for the target system and programming model. 

- ``ramble.yaml`` defines the `Ramble specs <https://googlecloudplatform.github.io/ramble/workspace_config.html#workspace-config>`_ for building, running, analyzing and archiving experiments. 
- ``execution_template.tpl`` serves as a template for the final experiment script that will be concretized and executed. 

A detailed description of Ramble configuration files is available at https://googlecloudplatform.github.io/ramble/workspace_config.html 
 
The different config files can be structured as a Ramble workspace as follows::

  cp -r ${APP_SOURCE_DIR}/configs/${SYSTEM}/* ${APP_WORKING_DIR}/workspace/configs 
  cp -r ${APP_SOURCE_DIR}/experiments/amg2023/openmp/* ${APP_WORKING_DIR}/workspace/configs 

 
