# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Ior(SpackApplication):
    """Ior benchmark"""
    name = "ior"

    tags = ['asc','engineering','hypre','solver','cfd','large-scale',
            'multi-node','single-node','mpi','network-latency-bound',
            'network-collectives','unstructured-grid']

    executable('p', 'ior', use_mpi=True)

    workload('ior', executables=['p'])
    #TODO: build FOMs. ior measures "throughput", but not sure how to calculate that from results
    figure_of_merit('Major kernels total time',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'Major kernels total time \(seconds\):\s+(?P<fom>[0-9]+\.[0-9]*(e^[0-9]*)?)',
                    group_name='fom', units='seconds')

    success_criteria('pass', mode='string', match=r'Major kernels total time', file='{experiment_run_dir}/{experiment_name}.out')
