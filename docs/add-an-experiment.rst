==================
Add an Experiment
==================
  
Experiment specifications are located in ``$benchpark/experiments``. 
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
