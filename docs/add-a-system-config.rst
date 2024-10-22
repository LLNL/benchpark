.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

=====================
Adding a System 
=====================

This guide is intended for those wanting to run a benchmark on a new system,
such as vendors, system administrators, or application developers. It assumes
a system specification does not already exist.

System specifications include details like:

- How many CPUs are there per node on the system
- What pre-installed MPI/GPU libraries are available

A system description is a ``system.py`` file, where Benchpark provides the API
where you can represent a systems as an object and customize the description with command line arguments.

------------------------------
Identifying a Similar System
------------------------------

The easiest place to start when configuring a new system is to find the closest similar
one that has an existing configuration already. Existing system configurations are listed
in the table in :doc:`system-list`. 

If you are running on a system with an accelerator, find an existing system with the same accelerator vendor,
and then secondarily, if you can, match the actual accererator. 

1. accelerator.vendor
2. accelerator.name

Once you have found an existing system with a similar accelerator or if you do not have an accelerator, 
match the following processor specs as closely as you can. 

1. processor.name
2. processor.ISA 
3. processor.uArch

For example, if your system has an NVIDIA A100 GPU and an Intel x86 Icelake CPUs, a similar config would share the A100 GPU, and CPU architecture may or may not match.
Or, if I do not have GPUs and instead have SapphireRapids CPUs, the closest match would be another system with x86_64, Xeon Platinum, SapphireRapids.

If there is not an exact match that is okay, steps for customizing are provided below.

-------------------------------------------------
Editing an Existing System to Match
-------------------------------------------------

.. note:
  make all these x86 example. Automate the directory structure?

If you want to add support for a new system you can add a class definition
for that system in a separate directory in ``var/sys_repo/systems/``. 
The best way is to copy the system.py for the most similar system identified above, and then paste it in a new directory and update it.
For example the genericx86 system is defined in::

  $benchpark
  ├── var
     ├── sys_repo
        ├── systems
           ├── genericx86
              ├── system.py


.. note:
  TODO: example with x86, show new hardware (GPU), compiler. Check the base class for other configurations, can we add docs to system.py and pull them in here?

.. literalinclude:: ../lib/benchpark/system.py
   :language: python

The main driver for configuring a system is done by defining a subclass for that system in a ``var/sys_repo/{SYSTEM}/system.py`` file, which inherits from the System base class defined in ``/lib/benchpark/system.py``.

As is, the x86_64 system subclass should work for most x86_64 systems, but potential common changes might be to edit the number of cores per cpu, compiler locations, or adding external packages.

.. note:
  TODO: Examples of making these changes...

Once the system subclass is written with proper configurations run: 
``./benchpark system init --dest </path/to/destination/folder> x86_64``

This will generate the required yaml configurations for your system and you can validate it works with a static experiment test.

------------------------
Validating the System
------------------------

To manually validate your new system, you should initialize it and run an existing experiment such as saxpy. For example::

  ./bin/benchpark system init --dest=test-new-system {SYSTEM}
  ./bin/benchpark experiment init --dest=saxpy saxpy
  ./bin/benchpark setup ./saxpy ./test-new-system workspace/

Then you can run the commands provided by the output, the experiments should be built and run successfully without any errors. 

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


Once you can run an experiment successfully, and the yaml looks correct the new system has been validated and you can continue your :doc:`benchpark-workflow`.


