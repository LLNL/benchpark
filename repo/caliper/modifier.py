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

    mode('time', description='Mode for collecting time')

    env_var_modification('CALI_CONFIG', 'runtime-report(output={experiment_run_dir}/{experiment_name}.cali)', method='set', modes=['time'])

    software_spec('caliper', spack_spec='caliper')

    required_package('caliper')

    #figure_of_merit_context('APS Executable',
    #                        regex=r'APS Results for executable (?P<exec_name>\w+)',
    #                        output_format='APS on {exec_name}')

    elapsed_time_regex = r'main\s*[0-9]+\.[0-9]+\s*[0-9]+\.[0-9]+\s*(?P<time>[0-9]+\.[0-9])+\s*[0-9]+\.[0-9]+'
    #FIXME: Use Caliper post-processing to extracct FOM
    figure_of_merit('Total Elapsed Time', fom_regex=elapsed_time_regex, group_name='time',
                    units='s', log_file='{experiment_run_dir}/{experiment_name}.cali') #, contexts=['APS Executable'])
