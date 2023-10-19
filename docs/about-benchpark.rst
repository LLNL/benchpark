=========
benchpark
=========

Benchpark is an open collaborative repository for reproducible specifications of HPC benchmarks.
Benchpark enables cross-site collaboration on benchmarking by providing a mechanism for sharing
reproducible, working specifications for the following:

1. **System specifications** 

- location of system compilers and system MPI
- system scheduler and launcher

2. **Benchmark specifications**

- source repo and version
- build (Spack) configuration
- run (Ramble) configuration 

3. **Experiment specifications**

- programming models to use for benchmarks on a given system type
- valid experiments for benchmarks on a given system (scientific parameter studies, performance parameter studies, etc.)

Dependencies
------------
Benchpark uses the following open source projects for specifying configurations:

* `Ramble <https://github.com/GoogleCloudPlatform/ramble>`_ ro specify run configurations
* `Spack <https://github.com/spack/spack>`_ to specify build configurations
