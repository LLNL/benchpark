# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Phloem(ExecutableApplication):
    """Phloem benchmark"""
    name = "Phloem"

    executable('p1', 'sqmr  --num_cores={num_cores} --num_nbors={num_nbors}', use_mpi=True)
    executable('p2', 'mpiBench', use_mpi=True)
    workload('sqmr', executables=['p1'])
    workload('mpiBench', executables=['p2'])

    workload_variable('num_cores', default='1',
                      description='Number of MPI ranks on the core node, correlates to number of cores on one compute node.',
                      workloads=['sqmr'])

    workload_variable('num_nbors', default='1',
                      description='Number of distinct neighbors to each rank on the core node.',
                      workloads=['sqmr'])

    figure_of_merit('RR Two-sided Lat (8 B)',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'\|\s+RR Two-sided Lat \(8 B\)+\|\s+(?P<fom>[0-9]+\.[0-9]*([0-9]*X)?)',
                   group_name='fom', units='usec')
    success_criteria('pass', mode='string', match=r'.*', file='{experiment_run_dir}/{experiment_name}.out')
