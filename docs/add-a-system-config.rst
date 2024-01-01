.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

=============================
Adding a System Configuration
=============================

``benchpark/configs`` contains a directory for each system specified in Benchpark.
If your system is unlike the available configurations,
you can add a new directory with a name which identifies the system.

The naming convention for the systems is as following::

  [INTEGRATOR]-MICROARCHITECTURE[-GPU][-NETWORK]

where::

  INTEGRATOR = COMPANY[_PRODUCTNAME][...]

Benchpark has definitions for the following systems:

- AWS_PCluster_Hpc7a-zen4-EFA

- HPECray-zen3-MI250X-Slingshot	(Frontier, Lumi, Tioga)

- IBM-power9-V100-Infiniband	(Sierra)

- Penguin-icelake-OmniPath

- x86_64                        (generic x86 CPU only platform)

The following files are required for each system ``benchpark/configs/${SYSTEM}``:

1. ``system_definition.yaml`` describes the system hardware, including the integrator (and the name of the product node or cluster type), the processor, (optionally) the accelerator, and the network; the information included here is what you will typically see recorded about the system on Top500.org.  We intend to make the system definitions in Benchpark searchable, and will add a schema to enforce consistency; until then, please copy the file and fill out all of the fields without changing the keys.  Also listed is the specific system the config was developed and tested on, as well as the known systems with the same hardware so that the users of those systems can find this system specification.

.. code-block:: yaml

  system_definition:
    name: HPECray-zen3-MI250X-Slingshot
    integrator:
      vendor: HPECray
      name: EX235a
    processor:
      vendor: AMD
      name: EPYC-Zen3
      ISA: x86_64
      uArch: zen3
    accelerator:
      vendor: AMD
      name: MI250X
      ISA: GCN
      uArch: gfx90a
    interconnect:
      vendor: HPECray
      name: Slingshot11
    system-tested:
      site: LLNL
      name: tioga
      installation-year: 2022
      description: [top500](https://www.top500.org/system/180052)
    top500-system-instances:
      - Frontier (ORNL)
      - Lumi     (CSC)
      - Tioga    (LLNL)


2. ``spack.yaml`` defines default compiler and package names Spack should
use to build the benchmarks on this system.  ``spack.yaml`` becomes the
spack section in the `Ramble configuration file
<https://googlecloudplatform.github.io/ramble/configuration_files.html#spack-config>`_.

.. code-block:: yaml

    spack:
      packages:
        default-compiler:
          spack_spec: 'spack_spec_for_package'
        default-mpi:
          spack_spec: 'spack_spec_for_package'

3. ``variables.yaml`` defines system-specific launcher and job scheduler.

.. code-block:: yaml

    variables:
      mpi_command: 'mpirun -N {n_nodes} -n {n_ranks}'
      batch_submit: '{execute_experiment}'
      batch_nodes: ''
      batch_ranks: ''
      batch_timeout: ''

4. Optionally, one can add more information about the software installed on the system
by adding Spack config files in ``benchpark/configs/${SYSTEM}/auxiliary_software_files/``.

- `compilers.yaml <https://spack.readthedocs.io/en/latest/getting_started.html#compiler-config>`_ defines the compilers installed on the system.
- `packages.yaml <https://spack.readthedocs.io/en/latest/build_settings.html#package-settings-packages-yaml>`_ defines the pre-installed packages  (e.g., system MPI) on the system.  One way to populate this list is to find available external packages: `spack external <https://spack.readthedocs.io/en/v0.21.0/command_index.html#spack-external>`. 
