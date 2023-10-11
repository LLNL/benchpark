======================
Adding a System Config
======================

System descriptions are located in ``configs/``. Each system type is
added as a subdirectory. If your system is not covered by
any of the existing descriptions, you can add a new directory.

This directory contains:

- `spack.yaml  <https://googlecloudplatform.github.io/ramble/configuration_files.html#spack-config>`_: this is a Ramble configuration file

  - Minimally (for the ``openmp`` experiments), you will need to define ``default-compiler`` and ``default-mpi``, which all the ``ramble.yaml`` files in ``experiments/`` use.
  - Benchpark adds this to a `scope <https://googlecloudplatform.github.io/ramble/configuration_files.html#configuration-scopes>`_ that is automatically used by Ramble
- `variables.yaml  <https://googlecloudplatform.github.io/ramble/configuration_files.html#variables-section>`_: also a Ramble configuration file; minimally (for the ``openmp`` experiments), this is used to explain to Ramble how to dispatch batch jobs on the system.

  - For the ``cuda`` experiments, this should also define ``cuda_version``
- auxiliary_software_files
  - You can describe pre-existing system resources here, including compilers and already-installed packages (`compilers.yaml <https://spack.readthedocs.io/en/latest/getting_started.html#compiler-config>`_ and `packages.yaml <https://spack.readthedocs.io/en/latest/build_settings.html#package-settings-packages-yaml>`_, respectively).

