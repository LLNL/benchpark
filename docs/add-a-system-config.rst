======================
Adding a System Configuration
======================

System descriptions are located in ``configs/``. Each system type is
added as a subdirectory. If your system is not covered by
any of the existing descriptions, you can add a new directory.
This directory name should identify the system.

**System specification:** Configuration files required by Spack to build the code on the target system, and for Ramble to run on the target system, are located in ``$benchpark/configs``. The following is required for each given system ``${SYSTEM}``:

1. ``spack.yaml`` defines compiler and package names Ramble will instruct Spack to use.

  - `spack.yaml  <https://googlecloudplatform.github.io/ramble/configuration_files.html#spack-config>`_ is a Ramble configuration file for Ramble.
  - Minimally (e.g., for the ``openmp`` experiments), you need to define ``default-compiler`` and ``default-mpi``.  These will be used in ``experiments/ramble.yaml`` files.
  - Benchpark adds `spack.yaml`` to a `scope <https://googlecloudplatform.github.io/ramble/configuration_files.html#configuration-scopes>`_ that is automatically used by Ramble

2. ``variables.yaml`` defines system-specific launcher and job scheduler.

  - `variables.yaml  <https://googlecloudplatform.github.io/ramble/configuration_files.html#variables-section>`_ is also a Ramble configuration file.
  - Minimally (e.g., for the ``openmp`` experiments), ``variables.yaml`` provides instructions on how to dispatch batch jobs on the system.
  - For the ``cuda`` experiments, ``variables.yaml`` should also define ``cuda_version`` to use on the system.

3. ``auxiliary_software_files/compilers.yaml`` and ``auxiliary_software_files/packages.yaml`` are used to describe software installed on the system:

  - `compilers.yaml <https://spack.readthedocs.io/en/latest/getting_started.html#compiler-config>`_ defines the compilers installed on the system.
  - `packages.yaml <https://spack.readthedocs.io/en/latest/build_settings.html#package-settings-packages-yaml>`_ defines the pre-installed packages  (e.g., system MPI) on the system.

 
 







3. 

