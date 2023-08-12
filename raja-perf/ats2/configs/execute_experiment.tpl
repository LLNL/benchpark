#!/bin/bash
#BSUB -nnodes {n_nodes}
#BSUB -W {batch_time}

cd {experiment_run_dir}

{spack_setup}

{command}
