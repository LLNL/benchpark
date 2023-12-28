# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from ramble.appkit import *

import sys

class LBANN(SpackApplication):
    """LBANN benchmark"""
    name = "lbann"

    tags = ["lbann"]

    executable('p1', 'lbann' +
                     ' -P {px} {py} {pz}' +
                     ' -n {nx} {ny} {nz}' +
                     ' -problem 1'        +
                     ' -keepT', use_mpi=True)

    executable('p2', 'lbann' +
                     ' -P {px} {py} {pz}' +
                     ' -n {nx} {ny} {nz}' +
                     ' -problem 2'        +
                     ' -keepT', use_mpi=True)

    workload('problem1', executables=['p1'])
    workload('problem2', executables=['p2'])

    workload_variable('px', default='2',
                      description='px',
                      workloads=['problem1', 'problem2'])
    workload_variable('py', default='2',
                      description='py',
                      workloads=['problem1', 'problem2'])
    workload_variable('pz', default='2',
                      description='pz',
                      workloads=['problem1', 'problem2'])
    workload_variable('nx', default='220',
                      description='nx',
                      workloads=['problem1', 'problem2'])
    workload_variable('ny', default='220',
                      description='ny',
                      workloads=['problem1', 'problem2'])
    workload_variable('nz', default='220',
                      description='nz',
                      workloads=['problem1', 'problem2'])

    figure_of_merit('Figure of Merit (FOM)', log_file='{experiment_run_dir}/{experiment_name}.out', fom_regex=r'Figure of Merit \(FOM\):\s+(?P<fom>[0-9]+\.[0-9]*(e^[0-9]*)?)', group_name='fom', units='')

    #TODO: Fix the FOM success_criteria(...)
    success_criteria('pass', mode='string', match=r'Figure of Merit \(FOM\)', file='{experiment_run_dir}/{experiment_name}.out')

    def evaluate_success(self):
      return True
