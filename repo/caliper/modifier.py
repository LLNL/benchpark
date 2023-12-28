# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from ramble.modkit import *


class Caliper(SpackModifier):
    """Define a modifier for Caliper"""

    name = "caliper"

    tags('profiler', 'performance-analysis')

    maintainers('olgapearce')

    mode('spot', description='Mode for collecting time only')

    mode('spot-topdown', description='Mode for collecting time only')

    mode('spot-cuda', description='Mode for collecting time only')

    _cali_datafile = '{experiment_run_dir}/{experiment_name}.cali'

    env_var_modification('CALI_CONFIG', 'spot(output={})'.format(_cali_datafile), method='set', modes=['spot'])

    env_var_modification('CALI_CONFIG', 'spot(output={}, topdown.all)'.format(_cali_datafile), method='set', modes=['spot-topdown'])

    env_var_modification('CALI_CONFIG', 'spot(output={}, profile.cuda)'.format(_cali_datafile), method='set', modes=['spot-cuda'])

    archive_pattern(_cali_datafile)

    software_spec('caliper', spack_spec='caliper')

    required_package('caliper')
