For each ``experiment`` (``benchmark`` x ``ProgrammingModel`` x ),
Ramble sets up the following ``workspace`` directory structure
to build and run the experiment::

    experiments_root/
        ramble/
        spack/
        <benchmark>/
            <ProgrammingModel>/
                <system>/
                    workspace/
                        configs/
                            (everything from source/configs/<system>)
                            (everything from source/experiments/<benchmark>)
                        experiments/
                            <benchmark>/
                                <problem>/
                                    <benchmark>_<ProgrammingModel>_<problem>
                                        execute_experiment
