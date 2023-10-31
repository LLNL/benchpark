================
Build experiment
================

`Benchmark setup <docs/4-benchmark-setup.rst>`_ will output instructions to follow::

  cd <workspace_root>/<benchmark/ProgrammingModel>/<system>/workspace

  . <workspace_root>/<benchmark/ProgrammingModel>/<system>/spack/share/spack/setup-env.sh
  . <workspace_root>/<benchmark/ProgrammingModel>/<system>/ramble/share/ramble/setup-env.sh

  export SPACK_DISABLE_LOCAL_CONFIG=1

  ramble -D . workspace setup  

which will build the source code and set up following workspace directory structure::

    workspace_root/
        <benchmark>/
            <system>/
                spack/
                ramble/
                workspace/
                    configs/
                        (everything from source/configs/<system>)
                        (everything from source/experiments/<benchmark>)
                    experiments/
                        <benchmark>/
                            <problem>/   
                                <benchmark>_<ProgrammingModel>_<problem>
                                    execute_experiment
