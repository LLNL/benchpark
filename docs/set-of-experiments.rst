==============
Working with a set of experiments
==============

To keep the source code consistent while working with 
a set of ``experiments`` (several ``benchmark/ProgrammingModels`` x ``systems``),
one can consider working with a single ``Benchpark workspace``, which will ensure the same
clone of Spack, and the same clone of Ramble, will be used for all of the ``experiments`` in 
this set.  To work with a set of ``experiments`` based on a single clone of Spack and 
a single clone of Ramble, set up your experiments in the same /output/path/to/workspace_root::

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
