===============
Benchpark setup 
===============

Select a benchmark experiment to run, along with the programming model to use, and a system to run them on.
Also choose the workspace for your experiment::

  $ ./benchpark setup benchmark/ProgrammingModel system /output/path/to/workspace_root

where:

- ``benchmark/ProgrammingModel``: amg2023/openmp | amg2023/cuda | saxpy/openmp (available choices in benchpark/experiments)
- ``system``: ats2 | ats4 | cts1 (available choices in benchpark/configs)

This command will assemble a Ramble workspace 
with a configuration for the specified benchmark and system 
with the following directory structure::

    workspace_root/
        <benchmark>/
            <system>/
                spack/
                ramble/
                workspace/
                    configs/
                        (everything from source/configs/<system>)
                        (everything from source/experiments/<benchmark>)

``benchpark setup`` will output further instructions, please follow them::

  cd <workspace_root>/<benchmark/ProgrammingModel>/<system>/workspace

  . <workspace_root>/<benchmark/ProgrammingModel>/<system>/spack/share/spack/setup-env.sh
  . <workspace_root>/<benchmark/ProgrammingModel>/<system>/ramble/share/ramble/setup-env.sh

  export SPACK_DISABLE_LOCAL_CONFIG=1

  ramble -D . workspace setup  

Each experiment has its own ``execute_experiment`` script which 
will set input paramaters and environment variables, run the experiment, and generate the output::

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

