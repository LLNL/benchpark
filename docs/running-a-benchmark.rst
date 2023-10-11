=================================
Running a benchmark in Benchpark
=================================
After installing Benchpark, select a benchmark experiment to run on a specified system type.

Benchpark experiments are modeled as a `Ramble workspace <https://googlecloudplatform.github.io/ramble/workspace.html>`_ – a set of self-contained configuration files required to correctly build and execute those experiments.

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

In order to create a complete experiment specification on a target system, we require three sets of config files:

**System-specific** – These specs are located in ``$benchpark/configs``. These are Spack configuration files required to build the code on a given system e.g. ``ats4`` or ``cts1``. The user can either use an existing system configuration provided by benchpark for instance, ``$benchpark/configs/ats4`` or provide their own configuration at ``$benchpark/configs``. For a target system, files ``compilers.yaml`` and ``packages.yaml`` `provide <https://spack.readthedocs.io/en/latest/configuration.html>`_, respectively, the compilers and package definitions (e.g. MPI) required by Spack to build an application on that system. ``spack.yaml`` provides names for Spack compiler/packages specs that are used by Ramble to create its Spack environment. ``variables.yaml`` defines system-specific variables to be used by the experiments e.g. application launcher and job scheduler available on the system.

**Application-specific** – These specs are located in ``$benchpark/repo``. These are system-independent specifications for building and running an application. Spack needs a `package repository <https://spack.readthedocs.io/en/latest/repositories.html>`_ with `instructions  <https://spack-tutorial.readthedocs.io/en/latest/tutorial_packaging.html#creating-the-package-file>`_ to build and install an application and each of its dependent packages (e.g. ``$benchpark/repo/amg2023/package.py`` and ``$benchpark/repo/hypre/package.py``.) Similarly, Ramble needs an application repository that defines the benchmark input and run specification (e.g. $benchpark/repo/amg2023/application.py.) An application can either use the built-in repositories shipped with the default Spack/Ramble repos or define a new repository in ``$benchpark/repo``. For a custom repository, Spack and Ramble must be pointed to the location of the correct spec files as follows:

``spack repo add --scope=site $benchpark/repo
ramble repo add --scope=site $benchpark/repo``

The top-level ``repo.yaml`` provides a unique namespace for the benchpark repository.

**Experiment-specific** – These specs are located in ``$benchpark/experiments``. They are organized by the target "backend" for the experiment e.g. ``$benchpark/experiment/amg2023/cuda`` for a CUDA-based experiment and ``$benchpark/experiment/amg2023/openmp`` for an OpenMP-bassed experiment. These files, in conjunction with the system configuration files and package/application repositories, are used to generate a set of concrete Ramble experiments for the target system and backend. ``ramble.yaml`` defines the `Ramble specs <https://googlecloudplatform.github.io/ramble/workspace_config.html#workspace-config>`_ for building, running, analyzing and archiving experiments. ``execution_template.tpl`` provides the template script from which the final experiment script to be executed is concretized.

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
