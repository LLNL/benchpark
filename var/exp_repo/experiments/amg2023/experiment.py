from benchpark.directives import variant
from benchpark.experiment import Experiment


class Amg2023(Experiment):
    variant(
        "programming_model",
        default="openmp",
        values=("openmp", "cuda", "rocm"),
        description="on-node parallelism model",
    )

    variant(
        "workload",
        default="problem1",
        values=("problem1", "problem2"),
        description="problem1 or problem2",
    )

    variant(
        "experiment",
        default="throughput",
        values=("strong", "weak", "throughput"),
        description="type of experiment",
    )

    def compute_applications_section(self):
        if self.spec.satisfies("workload=problem1"):
            self.workload = "problem1"
        else:
            self.workload = "problem2"

        px = "px"
        py = "py"
        pz = "pz"
        nx = "nx"
        ny = "ny"
        nz = "nz"
        num_procs = f"{{{px}}} * {{{py}}} * {{{pz}}}"

        variables = {}
        variables["n_ranks"] = num_procs

        # TODO: Use conditional variants
        # TODO: Implement supports for matrices, zips and excludes
        # TODO: Check for target system using programming_model mixin
        if self.spec.satisfies("programming_model=openmp"):
            variables["n_threads_per_proc"] = 1
            n_resources = "{n_ranks}_{n_threads_per_proc}"
        elif self.spec.satisfies("programming_model=cuda") or
             self.spec.satisfies("programming_model=rocm"):
            variables["n_gpus"] = num_procs
            n_resources = "{n_gpus}"

        experiment_name = f"amg2023_{self.spec.variants['programming_model'][0]}_{self.spec.variants['experiment'][0]}_{self.workload}_{{n_nodes}}_{n_resources}_{{{px}}}_{{{py}}}_{{{pz}}}_{{{nx}}}_{{{ny}}}_{{{nz}}}"

        experiment_setup = {}
        experiment_setup["variants"] = {"package_manager": "spack"}

        # Number of processes in each dimension
        initial_p = [2, 2, 2]
        variables[px] = initial_p[0]
        variables[py] = initial_p[1]
        variables[pz] = initial_p[2]    

        # Per-process size (in zones) in each dimension
        initial_n = [80, 80, 80]
        variables[nx] = initial_n[0]
        variables[ny] = initial_n[1]
        variables[nz] = initial_n[2]
        
        # TODO: Please explain the zips here.  Can we just declare this as a vector to begin with?
        zips_size = "size"
        experiment_setup["zips"] = {f"{zips_size}": [nx, ny, nz]}

        if self.spec.satisfies("programming_model=openmp"):
            experiment_setup["matrices"] = [
                {
                    "size_nodes_threads": [
                        f"{zips_size}",
                        "n_nodes",
                        "n_threads_per_proc",
                    ]
                   }
            ]
            experiment_setup["exclude"] = {
                "where": [
                    "{n_threads_per_proc} * {n_ranks} > {n_nodes} * {sys_cores_per_node}"
                ]
            }
        elif self.spec.satisfies("programming_model=cuda") or 
             self.spec.satisfies("programming_model=rocm"):
            experiment_setup["matrix"] = [f"{zips_size}"]
    
        # TODO: Is there an order these code blocks need to be in?  
        # Can the programming model part be completely separate from the scaling part?
        input_params = {}
        if self.spec.satisfies("experiment=throughput"):
            variables[px] = initial_p[0]
            variables[py] = initial_p[1]
            variables[pz] = initial_p[2]
            scaling_variable = (nx, ny, nz)
            input_params[scaling_variable] = initial_n
        elif self.spec.satisfies("experiment=strong"):
            scaling_variable = (px, py, pz)
            input_params[scaling_variable] = initial_p
            variables[nx] = initial_n[0]
            variables[ny] = initial_n[1]
            variables[nz] = initial_n[2]
        elif self.spec.satisfies("experiment=weak"):
            scaling_variable = (px, py, pz)
            input_params[scaling_variable] = initial_p
            input_params[(nx, ny, nz)] = initial_n
        variables |= self.scale_experiment_variables(
            input_params,
            int(self.spec.variants["scaling-factor"][0]),
            int(self.spec.variants["scaling-iterations"][0]),
            scaling_variable,
        )

        # TODO: Add explanation
        experiment_setup["variables"] = variables

        return {
            "amg2023": {
                "workloads": {
                    self.workload: {
                        "experiments": {
                            experiment_name: experiment_setup,
                        }
                    }
                }
            }
        }

    def compute_spack_section(self):
        app_name = self.spec.name

        # set package versions
        app_version = "develop"
        hypre_version = "2.31.0"
        # caliper_version = "master"

        # get system config options
        # TODO: Get compiler/mpi/package handles directly from system.py
        system_specs = {}
        system_specs["compiler"] = "default-compiler"
        system_specs["mpi"] = "default-mpi"
        system_specs["lapack"] = "lapack"
        if self.spec.satisfies("programming_model=cuda"):
            system_specs["cuda_version"] = "{default_cuda_version}"
            system_specs["cuda_arch"] = "{cuda_arch}"
            system_specs["blas"] = "cublas-cuda"
        if self.spec.satisfies("programming_model=rocm"):
            system_specs["rocm_arch"] = "{rocm_arch}"
            system_specs["blas"] = "blas-rocm"

        # set package spack specs
        package_specs = {}
        if self.spec.satisfies("programming_model=cuda"):
            package_specs["cuda"] = {
                "pkg_spec": "cuda@{}+allow-unsupported-compilers".format(
                    system_specs["cuda_version"]
                ),
                "compiler": system_specs["compiler"],
            }
            package_specs[system_specs["blas"]] = (
                {}
            )  # empty package_specs value implies external package
        if self.spec.satisfies("programming_model=rocm"):
            package_specs[system_specs["blas"]] = (
                {}
            )  # empty package_specs value implies external package
        package_specs[system_specs["mpi"]] = (
            {}
        )  # empty package_specs value implies external package
        package_specs[system_specs["lapack"]] = (
            {}
        )  # empty package_specs value implies external package
        package_specs["hypre"] = {
            "pkg_spec": f"hypre@{hypre_version} +mpi+mixedint~fortran",
            "compiler": system_specs["compiler"],
        }
        package_specs[app_name] = {
            "pkg_spec": f"amg2023@{app_version} +mpi",
            "compiler": system_specs["compiler"],
        }

        if self.spec.satisfies("programming_model=openmp"):
            package_specs["hypre"]["pkg_spec"] += "+openmp"
            package_specs[app_name]["pkg_spec"] += "+openmp"
        elif self.spec.satisfies("programming_model=cuda"):
            package_specs["hypre"]["pkg_spec"] += "+cuda cuda_arch={}".format(
                system_specs["cuda_arch"]
            )
            package_specs[app_name]["pkg_spec"] += "+cuda cuda_arch={}".format(
                system_specs["cuda_arch"]
            )
        elif self.spec.satisfies("programming_model=rocm"):
            package_specs["hypre"]["pkg_spec"] += "+rocm amdgpu_target={}".format(
                system_specs["rocm_arch"]
            )
            package_specs[app_name]["pkg_spec"] += "+rocm amdgpu_target={}".format(
                system_specs["rocm_arch"]
            )

        return {
            "packages": {k: v for k, v in package_specs.items() if v},
            "environments": {app_name: {"packages": list(package_specs.keys())}},
        }
