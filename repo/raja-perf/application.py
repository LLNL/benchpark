# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class RajaPerf(SpackApplication):
    """RAJA Performance suite"""
    name = "raja-perf"

    tags = ['asc','single-node','sub-node','structured-grid',
            'atomics','simd','vectorization','register-pressure',
            'high-memory-bandwidth','regular-memory-access',
            'mpi','network-point-to-point','network-latency-bound',
            'c++','raja','cuda','hip','openmp','sycl']

    executable('run', 'raja-perf.exe', use_mpi=True)

    workload('suite', executables=['run'])

    figure_of_merit('All tests pass', log_file='{experiment_run_dir}/{experiment_name}.out', fom_regex=r'(?P<tpass>DONE)!!!...', group_name='tpass', units='')

    success_criteria('pass', mode='string', match=r'DONE!!!....', file='{experiment_run_dir}/{experiment_name}.out')
