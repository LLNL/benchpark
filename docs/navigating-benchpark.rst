===================
Benchpark workspace
===================

Benchpark experiments are organized as a workspace, 
a set of self-contained configuration files required 
to correctly build and execute those experiments. 
 
Configuration files are organized as follows:: 

  ${APP_SOURCE_DIR} 
  ├── configs 
  │  ├── ${SYSTEM} 
  │  │  ├── auxiliary_software_files 
  │  │  │  ├── compilers.yaml 
  │  │  │  └── packages.yaml 
  │  │  ├── spack.yaml 
  │  │  └── variables.yaml 
  ├── experiments 
  │  ├── amg2023 
  │  │  ├── cuda 
  │  │  │  ├── execute_experiment.tpl 
  │  │  │  └── ramble.yaml 
  │  │  ├── openmp 
  │  │  │  ├── execute_experiment.tpl 
  │  │  │  └── ramble.yaml 
  └── repo 
     ├── amg2023 
     │  ├── application.py 
     │  └── package.py 
     └── repo.yaml 


A complete experiment specification requires three types of config files:  

1. **System specification:** Configuration files required by Spack to build the code on the target system. The following is required for each given system ``${SYSTEM}``:

  - ``compilers.yaml`` define the compilers on the system.
  - ``packages.yaml`` define the pre-installed packages  (e.g., system MPI) on the system.
  - ``spack.yaml`` defines names for Spack compiler and package specs. 
  - ``variables.yaml`` defines system-specific launcher and job scheduler. 
 
2. **Benchmark specification:** Specifications for building and running an application/benchmark, independent of the target system. The following is required for each benchmark: 

  - ``package.py`` is a Spack specification that defines how to build and install the benchmark.
  - ``application.py`` is a Ramble specification that defines the benchmark input and parameters.

By default, benchmark specifications provided in the Spack and Ramble repos will be used.
The user can override these default benchmark specifications by providing custom specifications in Benchpark, 
and pointing Spack and Ramble to these custom specifications instead::
  spack repo add --scope=site ${APP_SOURCE_DIR}/repo 
  ramble repo add --scope=site ${APP_SOURCE_DIR}/repo 

Note that the ``${APP_SOURCE_DIR}/repo`` needs a ``repo.yaml`` to distinguish the application’s spec 
from the default Spack/Ramble spec for the same application, if one exists. 


3. **Experiment specification:** 

  - ``ramble.yaml`` defines the specs for building, running, analyzing and archiving experiments. 
  - ``execution_template.tpl`` serves as a template for the actual experiment script that will be executed. 

A detailed description of Ramble configuration files is available at https://googlecloudplatform.github.io/ramble/workspace_config.html 
 
The different config files can be structured as a Ramble workspace as follows::

  cp -r ${APP_SOURCE_DIR}/configs/${SYSTEM}/* ${APP_WORKING_DIR}/workspace/configs 
  cp -r ${APP_SOURCE_DIR}/experiments/amg2023/openmp/* ${APP_WORKING_DIR}/workspace/configs 

 
