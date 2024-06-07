cd {experiment_run_dir}

srun -N {n_nodes} -n {n_ranks} --mpi=pmix --export=ALL,FI_EFA_USE_DEVICE_RDMA=1,FI_PROVIDER="efa",OMPI_MCA_mtl_base_verbose=100
