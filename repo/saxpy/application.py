# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.appkit import *

import sys

class Saxpy(SpackApplication):
    """saxpy benchmark"""
    name = "saxpy"

    tags = ["saxpy"]

    executable('p', 'saxpy -n {n}', use_mpi=True)

    workload('problem', executables=['p'])

    workload_variable('n', default='1024', description='problem size', workloads=['problem'])

    figure_of_merit('Kernel {num} size', fom_regex=r'Kernel done \((?P<num>[0-9]+)\): (?P<size>[0-9]+)', group_name='size', units='')
    figure_of_merit("success", fom_regex=r'(?P<done>Kernel done)', group_name='done', units='')

    success_criteria('pass', mode='string', match=r'Kernel done', file='{experiment_run_dir}/{experiment_name}.out')
