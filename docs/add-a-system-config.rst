.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

=============================
Adding a System Specification
=============================

System specifications include details like

- How many CPUs are there per node on the system
- What pre-installed MPI/GPU libraries are available

A system description is a set of YAML files collected into a directory. Benchpark provides an API
where you can represent systems as objects and customize their description with command line arguments.

Using System API to Generate a System Description
-------------------------------------------------

System classes are defined in ``var/sys_repo``; once the class has been
defined, you can invoke ``benchpark system init`` to generate a system
configuration directory that can then be passed to ``benchpark setup``::

    benchpark system init --dest=tioga-system tioga rocm=551 compiler=cce ~gtl

where "tioga rocm=551 compiler=cce ~gtl" describes a config for Tioga that
uses ROCm 5.5.1 components, a CCE compiler, and MPI without GTL support.

If you want to add support for a new system you can add a class definition
for that system in a separate directory in ``var/sys_repo/systems/``. For
example the Tioga system is defined in::

  $benchpark
  ├── var
     ├── sys_repo
        ├── systems
           ├── tioga
              ├── system.py

The following yaml files are examples of what is generated for a system after it is initialized:

1. ``system_id.yaml`` describes the system hardware, including the integrator (and the name of the product node or cluster type), the processor, (optionally) the accelerator, and the network; the information included here is what you will typically see recorded about the system on Top500.org.  We intend to make the system definitions in Benchpark searchable, and will add a schema to enforce consistency; until then, please copy the file and fill out all of the fields without changing the keys.  Also listed is the specific system the config was developed and tested on, as well as the known systems with the same hardware so that the users of those systems can find this system specification.

.. code-block:: yaml

  system_definition:
    name: HPECray-zen3-MI250X-Slingshot # or site-specific name, e.g., Frontier at ORNL
    site:
    system: HPECray-zen3-MI250X-Slingshot
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


2. ``software.yaml`` defines default compiler and package names your package
manager (Spack) should use to build the benchmarks on this system.
``software.yaml`` becomes the spack section in the `Ramble configuration
file
<https://googlecloudplatform.github.io/ramble/configuration_files.html#spack-config>`_.

.. code-block:: yaml

    software:
      packages:
        default-compiler:
          pkg_spec: 'spack_spec_for_package'
        default-mpi:
          pkg_spec: 'spack_spec_for_package'

3. ``variables.yaml`` defines system-specific launcher and job scheduler.

.. code-block:: yaml

    variables:
      timeout: '30'
      scheduler: "slurm"
      sys_cores_per_node: "128"
      sys_gpus_per_node: "4"
      sys_mem_per_node unset
      max_request: "1000"  # n_ranks/n_nodes cannot exceed this
      n_ranks: '1000001'  # placeholder value
      n_nodes: '1000001'  # placeholder value
      batch_submit: "placeholder"
      mpi_command: "placeholder"
      # batch_queue: "pbatch"
      # batch_bank: "guest"


Example: Creating a New System:
------------------------

We provide an example of creating a new system, based on the generic_x86 system configurations. 

The main driver for configuring a system is done by defining a subclass for that system in a ``var/sys_repo/{SYSTEM}/system.py`` file, which inherits from the System base class defined in ``/lib/benchpark/system.py``.

As is, the x86_64 system subclass should work for most x86_64 systems, but potential common changes might be to edit the number of cores per cpu, compiler locations, or adding external packages.

TODO: Examples of making these changes...

Once the system subclass is written with proper configurations run: 
``./benchpark system init --dest </path/to/destination/folder> x86_64``

This will generate the required yaml configurations for your system and you now validate it works with a static experiment test.

Validating the System
------------------------

To manually validate your new system, you should initialize it and run an existing experiment such as saxpy. For example::
  
  ./bin/benchpark system init --dest=test-new-system {SYSTEM}
  ./bin/benchpark experiment init --dest=saxpy saxpy
  ./bin/benchpark setup ./saxpy ./test-new-system workspace/

Then you can run the commands provided by the output, the experiments should be built and run successfully without any errors. 

If you are contributing the system to our code repository you must add a passing dryrun test to the ``.github/workflows/run.yml`` file before
your pull request will be merged. 

For example:
TODO: Tioga Hash?

.. code-block:: yaml

  - name: Dry run dynamic saxpy on dynamic {SYSTEM}
    run: |
      ./bin/benchpark system init --dest=new-system {SYSTEM}
      ./bin/benchpark experiment init --dest=saxpy-openmp saxpy
      ./bin/benchpark setup ./saxpy ./new-system workspace/
      . workspace/setup.sh
      ramble \
        --workspace-dir workspace/saxpy/Tioga-975af3c/workspace \
        --disable-progress-bar \
        --disable-logger \
        workspace setup --dry-run


Once you can run an experiment successfully, the new system has been validated and you can continue your :doc:`3-benchpark-workflow`.