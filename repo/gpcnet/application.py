# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Gpcnet(ExecutableApplication):
    """GPCNet benchmark"""
    name = "GPCNet"

    executable('p1', 'network_test', use_mpi=True)
    executable('p2', 'network_load_test', use_mpi=True)
    workload('network_test', executables=['p1'])
    workload('network_load_test', executables=['p2'])

    figure_of_merit('TBD',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'.*',
                    group_name='fom', units='MiB/sec')
    success_criteria('pass', mode='string', match=r'.*', file='{experiment_run_dir}/{experiment_name}.out')
