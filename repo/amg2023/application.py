# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.appkit import *

import sys

class Amg2023(SpackApplication):
    """AMG2023 benchmark"""
    name = "amg2023"

    tags = ["amg2023"]

    executable('p1', 'amg' +
                     ' -P {px} {py} {pz}' +
                     ' -n {nx} {ny} {nz}' +
                     ' -problem 1'        +
                     ' -keepT', use_mpi=True)

    executable('p2', 'amg' +
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
