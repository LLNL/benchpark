#!/bin/bash
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

    mode('spot', description='Mode for collecting time')

    env_var_modification('CALI_CONFIG', 'spot(output={experiment_run_dir}/{experiment_name}.cali)', method='set', modes=['spot'])

    _log_file = '{experiment_run_dir}/.caliper_fom'
    _cali_datadir = '{experiment_run_dir}/{experiment_name}.cali'
    _target_fom_name = '{target_fom_name}'

    # This will feed into an external profiler/data aggregator
    # FIXME: Is this correct?
    archive_pattern('{experiment_run_dir}/{experiment_name}.cali')

    software_spec('caliper', spack_spec='caliper')

    required_package('caliper')

    figure_of_merit('{target_fom_name}', fom_regex='{target_fom_name} = (?P<fom>.*)', log_file=_log_file,
                    units='', group_name='fom')

    # FIXME: This should be provided by the system
    # Handle this in Spack?
    def _load_thicket(self):
        # the plot thickets!!!
        import matplotlib.pyplot as plt

        import sys
        import platform

        input_deploy_dir_str = "/usr/gapps/spot/dev/"
        machine = platform.uname().machine

        sys.path.append(input_deploy_dir_str + "/hatchet-venv/" + machine + "/lib/python3.9/site-packages")
        sys.path.append(input_deploy_dir_str + "/hatchet/" + machine)
        sys.path.append(input_deploy_dir_str + "/thicket-playground-dev")

    # TODO: add hooks to customize this function per experiment
    # add additional python scripts in configs?
    def _prepare_analysis(self, workspace):
        self._load_thicket()

        import hatchet as ht
        import thicket as tt

        with open(self.expander.expand_var(self._log_file), 'w+') as f:
            target_fom_name = self.expander.expand_var(self._target_fom_name)
            t_ens = tt.Thicket.from_caliperreader(self.expander.expand_var(self._cali_datadir))
            fom = t_ens.metadata[target_fom_name].iloc[0]
            f.write("{} = {:.6E}".format(target_fom_name, fom))
