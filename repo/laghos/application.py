# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Laghos(ExecutableApplication):
    """Laghos benchmark"""
    name = "laghos"

    tags = ['asc','engineering','hypre','solver','mfem','cfd','large-scale',
            'multi-node','single-node','mpi','c++','high-order','hydrodynamics',
            'explicit-timestepping','finite-element','time-dependent','ode',
            'full-assembly','partial-assembly',
            'lagrangian','spatial-discretization','unstructured-grid',
            'network-latency-bound','network-collectives','unstructured-grid']

    executable('prob', 'laghos -p {problem} -m {mesh} -rs {rs} -rp {rp} -ms {ms}', use_mpi=True)

    workload('problem', executables=['prob'])

    workload_variable('mesh', default='{laghos}/data/box01_hex.mesh',
            description='mesh file',
            workloads=['problem'])

    workload_variable('problem', default='3',
            description='problem number',
            workloads=['problem'])
        

    workload_variable('rs', default='5',
            description='number of serial refinements',
            workloads=['problem'])
    
    workload_variable('rp', default='0',
            description='number of parallel refinements',
            workloads=['problem'])
    workload_variable('ms', default='500',
            description='max number of steps',
            workloads=['problem'])

    figure_of_merit('Major kernels total time',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'Major kernels total time \(seconds\):\s+(?P<fom>[0-9]+\.[0-9]*(e^[0-9]*)?)',
                    group_name='fom', units='seconds')

    success_criteria('pass', mode='string', match=r'Major kernels total time', file='{experiment_run_dir}/{experiment_name}.out')
