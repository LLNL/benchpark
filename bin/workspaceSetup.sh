#!/bin/bash

#SBATCH -p pbatch
#SBATCH -A fractale
#SBATCH -t 5
#SBATCH --job-name=setup_workspace

ramble -P -D /usr/workspace/knox10/bm/helloworld/openmp/nosite-x86_64/workspace workspace setup

ramble -P -D /usr/workspace/knox10/bm/helloworld/openmp/nosite-x86_64/workspace on
