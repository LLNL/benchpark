===============
Benchpark setup 
===============

Select a benchmark experiment to run, along with the programming model to use, and a system to run them on.
Also choose the workspace for your experiment::

  $ ./benchpark setup benchmark/ProgrammingModel system /output/path/to/workspace_root

where:

- ``benchmark/ProgrammingModel``: amg2023/openmp | amg2023/cuda | saxpy/openmp (available choices in benchpark/experiments)
- ``system``: ats2 | ats4 | cts1 (available choices in benchpark/configs)

This command will assemble a Ramble workspace 
with a configuration for the specified benchmark and system 
with the following directory structure::

    workspace_root/
        <benchmark>/
            <system>/
                spack/
                ramble/
                workspace/
                    configs/
                        (everything from source/configs/<system>)
                        (everything from source/experiments/<benchmark>)

``benchpark setup`` will output 
`Build experiment <docs/5-build-experiment.rst>`_ instructions.
