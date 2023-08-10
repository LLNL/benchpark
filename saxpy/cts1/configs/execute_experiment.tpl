#!/bin/bash
#SBATCH -N {n_nodes}
#SBATCH -n {n_ranks}

cd {experiment_run_dir}

{spack_setup}

{command}
