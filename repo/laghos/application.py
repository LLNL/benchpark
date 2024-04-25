# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Laghos(SpackApplication):
    """Laghos benchmark"""
    name = "laghos"

    tags = ['asc','engineering','hypre','solver','cfd','large-scale',
            'multi-node','single-node','mpi','network-latency-bound',
            'network-collectives','unstructured-grid']

    executable('p', 'laghos -p 1 -dim 3 -rs 2 -tf 0.6 -pa', use_mpi=True)

    workload('problem', executables=['p'])

    figure_of_merit('Major kernels total time',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'Major kernels total time \(seconds\):\s+(?P<fom>[0-9]+\.[0-9]*(e^[0-9]*)?)',
                    group_name='fom', units='seconds')

    success_criteria('pass', mode='string', match=r'Major kernels total time', file='{experiment_run_dir}/{experiment_name}.out')
