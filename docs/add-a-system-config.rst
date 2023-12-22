=============================
Adding a System Configuration
=============================

``benchpark/configs`` contains a directory for each system specified in Benchpark.
If your system is unlike the available configurations,
you can add a new directory with a name which identifies the system.

The naming convention for the systems is as following::

  (opt)Integrator-(opt)ClusterType-CPU-(opt)GPU-Network

Benchpark has definitions for the following systems:
- AWS-Hpc7a-EPYC4-EFA
- HPECray-EPYC3-MI250X-Slingshot	(Frontier, Lumi, Tioga)
- IBM-POWER9-V100-Infiniband	        (Sierra, Summit)
- Penguin-XeonPlatinum-OmniPath
- x86_64                                (generic x86 CPU only platform)

The following files are required for each system ``benchpark/configs/${SYSTEM}``:

1. ``system_definition.yaml``

.. code-block:: yaml

  system_definition:
    name: HPECray-EPYC3-MI250X-Slingshot
    manufacturer:
      vendor: HPE-Cray
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
      vendor: HPE-Cray
      name: Slingshot-11
    OS:
      name: HPE-Cray-OS
    system-tested:
      owner: LLNL
      name: tioga
      installation-year: 2022
      description: [top500](https://www.top500.org/system/180052)
    top500-system-instances:
      - Frontier (ORNL)
      - Lumi (EuroHPC/CSC)
      - Tioga (LLNL)


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
- `packages.yaml <https://spack.readthedocs.io/en/latest/build_settings.html#package-settings-packages-yaml>`_ defines the pre-installed packages  (e.g., system MPI) on the system.
