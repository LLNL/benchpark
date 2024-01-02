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

    mode('spot-topdown', description='Top-down analysis for Intel CPUs (all levels)')

    mode('spot-cuda', description='Profile CUDA API functions')

    _cali_datafile = '{experiment_run_dir}/{experiment_name}.cali'

    env_var_modification('CALI_CONFIG', 'spot(output={})'.format(_cali_datafile), method='set', modes=['spot'])

    env_var_modification('CALI_CONFIG', 'spot(output={}, topdown.all)'.format(_cali_datafile), method='set', modes=['spot-topdown'])

    env_var_modification('CALI_CONFIG', 'spot(output={}, profile.cuda)'.format(_cali_datafile), method='set', modes=['spot-cuda'])

    archive_pattern(_cali_datafile)

    software_spec('caliper', spack_spec='caliper')

    required_package('caliper')
