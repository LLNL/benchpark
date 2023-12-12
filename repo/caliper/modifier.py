# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.modkit import *


class Caliper(SpackModifier):
    """Define a modifier for Caliper"""

    name = "caliper"

    tags('profiler', 'performance-analysis')

    maintainers('olgapearce')

    mode('spot', description='Mode for collecting time only')

    env_var_modification('CALI_CONFIG', 'spot(output={experiment_run_dir}/{experiment_name}.cali)', method='set', modes=['spot'])

    _log_file = '{experiment_run_dir}/.caliper_fom'
    _cali_datadir = '{experiment_run_dir}/{experiment_name}.cali'

    # This will feed into an external profiler/data aggregator
    # FIXME: Is this correct?
    archive_pattern('{experiment_run_dir}/{experiment_name}.cali')

    software_spec('caliper', spack_spec='caliper')

    required_package('caliper')
