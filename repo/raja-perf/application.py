# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.appkit import *

import sys

class RajaPerf(SpackApplication):
    """RAJA Performance suite"""
    name = "raja-perf"

    tags = ["raja-perf"]

    executable('run', 'raja-perf.exe', use_mpi=True)

    workload('suite', executables=['run'])

    figure_of_merit('All tests pass', log_file='{experiment_run_dir}/{experiment_name}.out', fom_regex=r'(?P<tpass>DONE)!!!...', group_name='tpass', units='')

    success_criteria('pass', mode='string', match=r'DONE!!!....', file='{experiment_run_dir}/{experiment_name}.out')
