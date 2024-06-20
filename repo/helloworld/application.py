import sys


from ramble.appkit import *
class Helloworld(SpackApplication):
    name="helloworld"

    tags = ['openmp']

    executable('p', 'helloworld -n {n}', use_mpi=True)

    workload('problem', executables=['p'])
    workload_variable('n', default='512', description='problem size', workloads=['problem'])
    #success_criteria("wrote_anything", mode="string", match=r".*")
    figure_of_merit("success", fom_regex=r'.*', group_name='done', units='')
    success_criteria('valid', mode='string', match=r'.*', file='{experiment_run_dir}/{experiment_name}.out')

