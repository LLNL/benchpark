==============
Working with a set of experiments
==============

You may want to use the same workspace_root directory when setting up multiple experiments:

* Benchpark only stores one copy of Spack/Ramble per workspace, and does not repeatedly
  download them when reusing a workspace.
* Since each experiment in the workspace shares the Spack/Ramble instances, the edits/updates
  you make to Spack packages will apply to all experiments in the workspace.

To use the same workspace_root directory when setting up multiple experiments,
instruct benchpark to set them up in the same workspace_root::

    benchpark setup benchmark1/ProgrammingModel1 system1 /output/path/to/workspace_root
    benchpark setup benchmark1/ProgrammingModel2 system2 /output/path/to/workspace_root
    benchpark setup benchmark2/ProgrammingModel2 system1 /output/path/to/workspace_root

This will result in the following directory structure::

    workspace_root/
        ramble/
        spack/
        benchmark1/
            ProgrammingModel1/
                system1/
                    workspace/
            ProgrammingModel2/
                system2/
                    workspace/
        benchmark2/
            ProgrammingModel2/
                system1/
                    workspace/

Note that there is a single clone of Ramble, and a single clone of Spack, 
which all of the ``experiments`` use.
Each ``experiment`` (``benchmark/ProgrammingModel`` x ``system`` combination)
has its own ``Ramble workspace``, where the ``experiment`` will be compiled and run.
