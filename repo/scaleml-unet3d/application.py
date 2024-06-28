# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class ScaleMLUNet3D(SpackApplication):
    """ScaleMLUNet3D benchmark"""
    name = "ScaleML-UNet3D"

    tags = ['ai',
            'large-scale','multi-node','single-node','sub-node',
            'mpi','c','cuda','hip']

    executable('p1', 'train.sh', 'configs/config.yml')

    workload('problem1', executables=['p1'])

    figure_of_merit('Figure of Merit (FOM)', log_file='{experiment_run_dir}/{experiment_name}.out', fom_regex=r'Figure of Merit \(FOM\):\s+(?P<fom>[0-9]+\.[0-9]*(e^[0-9]*)?)', group_name='fom', units='')

    #TODO: Fix the FOM success_criteria(...)
    success_criteria('pass', mode='string', match=r'Figure of Merit \(FOM\)', file='{experiment_run_dir}/{experiment_name}.out')
