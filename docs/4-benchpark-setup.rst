===============
Benchpark setup 
===============

Select a benchmark experiment to run, along with the programming model to use, and a system to run them on.
Also choose the workspace for your experiment::

  $ ./benchpark setup benchmark/ProgrammingModel system /output/path/to/workspace

where:

- ``benchmark/ProgrammingModel``: amg2023/openmp | amg2023/cuda | saxpy/openmp (available choices in benchpark/experiments)
- ``system``: ats2 | ats4 | cts1 (available choices in benchpark/configs)

This command will assemble a Ramble workspace 
with a configuration for the specified benchmark and system 
with the following directory structure::


    workspace_root/
        <benchmark>/
            <system>/
                workspace/
                    configs/
                        (everything from source/configs/<system>)
                        (everything from source/experiments/<benchmark>)
                spack/
                ramble/

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

Each workspace has its own ``execute_experiment`` script which 
will set input paramaters and environment variables, run the experiment, and generate the output.



What ``benchmark setup`` does
------------------------------------------------- 
``benchmark setup`` will set up a Ramble workspace,
build the benchmark, and generate run scripts for the benchmark.

1 Create an experiment directory at some location ``$workspace`` ::

  mkdir $workspace

2 Set up the required system-, application- and experiment-specific config files 
for your experiment 

3 (opt) If you are using non-upstreamed Spack package and/or Ramble application, 
you will need to point Spack and Ramble to the package and application 
in ``benchpark/repo``::

  spack repo add --scope=site $benchpark/repo
  ramble repo add --scope=site $benchpark/repo

4 Copy the required system and experiment config files to $workspace::

  cp -r $benchpark/configs/ats4/* $workspace/configs
  cp -r $benchpark/experiments/amg2023/cuda/* $workspace/configs


5 Build the benchmark using Spack, and generate run scripts for the experiment ::

    ramble -D . workspace setup
