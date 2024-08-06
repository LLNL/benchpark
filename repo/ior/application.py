# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Ior(ExecutableApplication):
    """Ior benchmark"""
    name = "ior"

    tags = ['asc','engineering','hypre','solver','cfd','large-scale',
            'multi-node','single-node','mpi','network-latency-bound',
            'network-collectives','unstructured-grid']

    executable('p', 'ior -Cge -wWr -F'+
            ' -b {b}' +
            ' -t {t}' +
            ' -a {a}'
            , use_mpi=True)

    workload('ior', executables=['p'])

    workload_variable('a', default='POSIX',
        description='api',
        workloads=['ior'])

    workload_variable('b', default='16m',
        description='blockSize -- contiguous bytes to write per task  (e.g.: 8, 4k, 2m, 1g)',
        workloads=['ior'])

    workload_variable('t', default='1m',
        description='transferSize -- size of transfer in bytes (e.g.: 8, 4k, 2m, 1g)',
        workloads=['ior'])

    workload_variable('N', default='1',
        description='numTasks -- number of tasks that are participating in the test (overrides MPI)',
        workloads=['ior'])
    #TODO: build FOMs. ior measures "throughput", but not sure how to calculate that from results
    figure_of_merit('Max write',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'Max Write:\s+(?P<fom>[0-9]+\.[0-9]*([0-9]*)?)',
                    group_name='fom', units='MiB/sec')

    figure_of_merit('Max read',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'Max Read:\s+(?P<fom>[0-9]+\.[0-9]*([0-9]*)?)',
                    group_name='fom', units='MiB/sec')
    success_criteria('pass', mode='string', match=r'.*', file='{experiment_run_dir}/{experiment_name}.out')
