==============
(optional) Edit experiment
==============

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

You can edit any of them to change the behaviour of your experiments.

compilers.yaml
--------------
If you would like to use a non-default compiler on your system, 
you can manually edit the specification in ``compilers.yaml``.

variables.yaml
--------------
If you would like to use non-default runtime behaviour on your system,
such as compiling in batch instead of on the login node, 
you can manually edit the specification in ``variables.yaml``.

ramble.yaml
--------------
If you would like to use modifiers on your system,
such as using Caliper to measure the performance of your experiments, 
you can manually edit the specification in ``ramble.yaml``.
