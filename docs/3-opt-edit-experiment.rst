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

System specification
-------------------
Files under ``benchpark/configs/${SYSTEM}`` provide the specification
of the software stack on your system
(see `Add a system config <add-a-system.rst>`_ for details).

Experiment specification
-------------------
Files under ``benchpark/experiments/${BENCHMARK}/${ProgrammingModel}``
provide the specifications for the experiments.
If you would like to make changes to your experiments,  such as enabling 
specific tools to measure the performance of your experiments, 
you can manually edit the specifications in ``ramble.yaml``
(see `Add an experiment <add-an-experiment.rst>`_ for details).

Benchmark specification
-------------------
If you would like to modify a specification of your benchmark,
you can do so by upstreaming changes to Spack and/or Ramble,
or working on your benchmark specification in ``benchpark/repo/${BENCHMARK}`` 
(see `Add a benchmark <add-a-benchmark.rst>`_ for details).
