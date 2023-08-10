#!/bin/bash
#BSUB -nnodes {n_nodes}
#BSUB -W {batch_time}

{module_purge}
{module_load}

cd {experiment_run_dir}

{spack_setup}

{experiment_setup} #TODO: Add experiment specific code here

{command}
