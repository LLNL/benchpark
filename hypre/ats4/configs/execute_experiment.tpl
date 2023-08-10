#!/bin/bash
#SBATCH -N {n_nodes}
#SBATCH -n {n_ranks}
#SBATCH -t {batch_time} 

{module_purge}
{module_load}

cd {experiment_run_dir}

{spack_setup}

{experiment_setup} #TODO: Add experiment specific code here

{command}
