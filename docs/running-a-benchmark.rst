=================================
Running a benchmark in Benchpark
=================================
After installing Benchpark, select a benchmark experiment to run on a specified system type.

Configuring Benchpark experiments
-----------------------------------------
The following steps should be followed to configure an experiment in Benchpark.

1. Clone the Benchpark repository at some location ``$benchpark``::

git clone git@github.com:LLNL/benchpark.git $benchpark

2. Add the required system-, application- and experiment-specific config files for the benchmark to ``$benchpark`` as described `above <docs/navigating-benchpark.rst>`_

3. Create an experiment directory at some location ``$workspace``_::

  mkdir $workspace

4. Clone the Spack and Ramble repositories. Skip this step if Spack/Ramble installation is already available::

  git clone --depth=1 -c feature.manyFiles=true https://github.com/spack/spack.git $workspace/spack
  git clone --depth=1 -c feature.manyFiles=true https://github.com/GoogleCloudPlatform/ramble.git $workspace/ramble

5. Source the Spack/Ramble shell scripts for your environment::

  . $workspace/spack/share/spack/setup-env.sh
  . $workspace/ramble/share/ramble/setup-env.sh

6. Clean the spack and Ramble environment::

  export SPACK_DISABLE_LOCAL_CONFIG=1
  rm -rf ~/.ramble/repos.yaml

7. Point Spack and Ramble to the Benchpark package and application repository::

  spack repo add --scope=site $benchpark/repo
  ramble repo add --scope=site $benchpark/repo

8. Copy the required system and experiment config files to $workspace ::

  cp -r $benchpark/configs/ats4/* $workspace/configs
  cp -r $benchpark/experiments/amg2023/cuda/* $workspace/configs

To simplify the configuration process, we provide a script with the Benchpark repository ``$benchpark/bin/benchpark``.
This script takes as input the system name, experiment programming model, and the location of the experiment directory, 
and sets the Spack and Ramble configurations appropriately::

  $benchpark/bin/benchpark amg2023/cuda ats4 $workspace


Building the benchmark and setting up a workspace
------------------------------------------------- 
This step builds the application using Spack::

  cd $workspace
  ramble -D . workspace setup

It also creates the set of concrete experiments to be executed. 
After workspace setup is complete, Ramble creates a ``$workspace/experiments`` 
directory with a unique subdirectory for each experiment instance::

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

Each instance has its own ``execute_experiment`` script which is used to set 
input paramaters and environment variables, run the experiment, and generate the output.

Run the experiment(s)
-----------------------------------------
This step runs all the experiments in the workspace::

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

  ramble -D . workspace analyze 

can be used to analyze figures of merit and evaluate 
`success/failure <https://googlecloudplatform.github.io/ramble/success_criteria.html>`_ 
of the experiments. Ramble generates a summary results file in ``$workspace``.

