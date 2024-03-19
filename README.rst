.. raw:: html

    <div align="left">
      <h2>
        <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/LLNL/benchpark/develop/docs/_static/images/benchpark-dark.svg" width="400">
        <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/LLNL/benchpark/develop/docs/_static/images/benchpark-light.svg" width="400">
        <img alt="Benchpark" src="https://raw.githubusercontent.com/LLNL/benchpark/develop/docs/_static/images/benchpark-light.svg" width="400">
        </picture>
      </h2>
    </div>

You can find detailed documentation at `software.llnl.gov/benchpark
<https://software.llnl.gov/benchpark>`_. Benchpark can also be found on `GitHub
<https://github.com/llnl/benchpark>`_.

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

* `Ramble <https://github.com/GoogleCloudPlatform/ramble>`_ to specify run configurations
* `Spack <https://github.com/spack/spack>`_ to specify build configurations

Community
---------
Benchpark is an open source project.  Questions, discussion, and contributions
of new benchmarks, experiments, and system specifications are welcome.
We use `github discussions <https://github.com/llnl/benchpark/discussions>`_ for Q&A and discussion.

Contributing
------------
To contribute to Benchpark, please open a `pull request
<https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests>`_
to the `develop` branch.  Your PR must pass Benchpark's unit tests, and must be `PEP 8 <https://peps.python.org/pep-0008/>`_ compliant.

Authors and citations
---------------------
Many thanks to Benchpark's `contributors <https://github.com/llnl/benchpark/graphs/contributors>`_.

Benchpark was created by Olga Pearce, Alec Scott, Greg Becker, Riyaz Haque, and Nathan Hanford.

To cite Benchpark, please use the following citation:

Olga Pearce, Alec Scott, Gregory Becker, Riyaz Haque, Nathan Hanford, Stephanie Brink,
Doug Jacobsen, Heidi Poxon, Jens Domke, and Todd Gamblin. 2023.
Towards Collaborative Continuous Benchmarking for HPC.
In Workshops of The International Conference on High Performance Computing,
Network, Storage, and Analysis (SC-W 2023), November 12–17, 2023, Denver, CO, USA.
ACM, New York, NY, USA, 9 pages.
`doi.org/10.1145/3624062.3624135 <https://doi.org/10.1145/3624062.3624135>`_.

License
-------
Benchpark is released under the Apache 2.0 w/ LLVM Exception license. For more
details see the [LICENSE](./LICENSE) file.

LLNL-CODE-850629
