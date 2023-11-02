================
Build experiment
================

``benchpark setup`` has set up the directory structure for your experiment.  
The next step is setting up the Ramble workspace and building the code::

   cd <workspace_root>/<benchmark/ProgrammingModel>/<system>/workspace
   ramble -P -D . workspace setup  


Ramble will build the source code and set up the following workspace directory structure::

    workspace_root/
        <benchmark>/
            <ProgrammingModel>/
                <system>/
                    ramble/
                    spack/
                    workspace/
                        configs/
                            (everything from source/configs/<system>)
                            (everything from source/experiments/<benchmark>)
                        experiments/
                            <benchmark>/
                                <problem>/
                                    <benchmark>_<ProgrammingModel>_<problem>
                                        execute_experiment


If you change any build instructions, rerun the `ramble -P -D . workspace setup` command
to re-setup the workspace and rebuild the binaries as necessary.
