=================================
Running an Experiment in Benchpark
=================================

To run all of the experiments in the workspace::

  ramble -D . on

An output file is generated for each experiment in its unique directory::

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

An experiment instance can also be executed individually by directly invoking its ``execute_experiment`` script 
(e.g., ``$workspace/experiments/amg2023/problem1/amg2023_cuda11.8.0_problem1_1_8_2_2_2_10_10_10/execute_experiment``).
Note that rerunning the experiment may overwrite any existing output files in the directory.

Analyze the experiment results 
-----------------------------------------
Once the experiments have been run, the command:: 

  ramble -P -D . workspace analyze 

can be used to analyze figures of merit and evaluate 
`success/failure <https://googlecloudplatform.github.io/ramble/success_criteria.html>`_ 
of the experiments. Ramble generates a summary results file in ``$workspace``.

