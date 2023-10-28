======================
Adding a System Configuration
======================

``benchpark/configs`` contains a directory for each system specified in Benchpark.
If the software stack on your system is unlike the available configurations, 
you can add a new directory with a name which identifies the system.

The following is required for each given system ``benchpark/configs/${SYSTEM}``:

1. ``spack.yaml`` defines default compiler and package names Spack should
use to build the benchmarks on this system.  ``spack.yaml`` becomes the
spack section in the `Ramble configuration file 
<https://googlecloudplatform.github.io/ramble/configuration_files.html#spack-config>`_.
Minimally, you need to define ``default-compiler`` and ``default-mpi``.  

.. code-block:: yaml

    spack:
      concretized: [True/False] # Should be false unless defined in a concretized workspace
      [variables: {}]
      packages:
        <package_name>:
          spack_spec: 'spack_spec_for_package'
          compiler_spec: 'Compiler spec, if different from spack_spec' # Default: None
          compiler: 'package_name_to_use_as_compiler' # Default: None
          [variables: {}]
          [matrix:]
          [matrices:]
      environments:
        <environment_name>:
          packages:
          - list of
          - packages in
          - environment
          [variables: {}]
          [matrix:]
          [matrices:]
        <external_env_name>:
          external_spack_env: 'name_or_path_to_spack_env'

2. ``variables.yaml`` defines system-specific launcher and job scheduler.
`variables.yaml  <https://googlecloudplatform.github.io/ramble/configuration_files.html#variables-section>`_ is a Ramble configuration file.

..  literalinclude:: /configs/x86/variables.yaml
    :language: yaml
    :emphasize-lines: 1,3-4
    :linenos:

3. Optionally, one can add more information about the software installed on the system in 
``benchpark/configs/auxiliary_software_files``.

  - `compilers.yaml <https://spack.readthedocs.io/en/latest/getting_started.html#compiler-config>`_ defines the compilers installed on the system.
  - `packages.yaml <https://spack.readthedocs.io/en/latest/build_settings.html#package-settings-packages-yaml>`_ defines the pre-installed packages  (e.g., system MPI) on the system.
