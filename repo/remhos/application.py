# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Remhos(ExecutableApplication):
    """Remhos benchmark"""
    name = "remhos"



    executable('run', 'remhos'+' -m {mesh}'+' -p {p}'+' -rs {rs}'+'{rp}'+' -dt {dt}'+' -tf {tf}'+' -ho {ho}' ' -lo {lo}'+' -fct {fct}', use_mpi=True)

    workload('remhos', executables=['run'])
    
    workload_variable('mesh', default='{remhos}/data/periodic-square.mesh',
        description='mesh',
        workloads=['remhos'])

    workload_variable('p', default='5',
        description='p',
        workloads=['remhos'])
    
    workload_variable('rs', default='3',
        description='rs',
        workloads=['remhos'])
    
    workload_variable('rp', default='',
        description='rp',
        workloads=['remhos'])

    workload_variable('dt', default='0.005',
        description='dt',
        workloads=['remhos'])

    workload_variable('tf', default='0.8',
        description='tf',
        workloads=['remhos'])
    
    workload_variable('ho', default='1',
        description='ho',
        workloads=['remhos'])

    workload_variable('lo', default='2',
        description='lo',
        workloads=['remhos'])

    workload_variable('fct', default='2',
        description='fct',
        workloads=['remhos'])
    #FOM_regex=r'(?<=Merit)\s+[\+\-]*[0-9]*\.*[0-9]+e*[\+\-]*[0-9]*'
    figure_of_merit("success", log_file='{experiment_run_dir}/{experiment_name}.out', fom_regex=r'(?P<done>.*)', group_name='done', units='')
    success_criteria('valid', mode='string', match=r'.*', file='{experiment_run_dir}/{experiment_name}.out')

