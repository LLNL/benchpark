.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

======================================
Adding a Specific System Specification
======================================

For a specific system, one can (optionally) add more information about the software installed on the system
by adding Spack config files in ``benchpark/configs/$SITE/SYSTEMNAME-GENERICSYSTEM/auxiliary_software_files/``.

- ``compilers.yaml`` defines the `compilers <https://spack.readthedocs.io/en/latest/getting_started.html#compiler-config>`_  installed on the system.
- ``packages.yaml`` defines the pre-installed `packages <https://spack.readthedocs.io/en/latest/build_settings.html#package-settings-packages-yaml>`_   (e.g., system MPI) on the system.  One way to populate this list is to find available external packages: `spack external <https://spack.readthedocs.io/en/v0.21.0/command_index.html#spack-external>`_.
