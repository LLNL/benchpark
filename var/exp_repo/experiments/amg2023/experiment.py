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
        description="problem1 or problem2",
    )

    variant(
        "experiment",
        default="example",
        values=("strong", "weak", "example"),
        description="type of experiment",
    )

    variant(
        "caliper",
        default="none",
        values=("none", "time", "mpi", "cuda", "topdown-counters-all", "topdown-counters-toplevel", "topdown-all", "topdown-toplevel"),
        description="caliper mode",
    )

    # TODO: Support list of 3-tuples
    # variant(
    #     "p",
    #     description="value of p",
    # )

    # TODO: Support list of 3-tuples
    # variant(
    #     "n",
    #     description="value of n",
    # )

    def make_experiment_example(self):
        app_name = self.spec.name

        variables = {}
        matrices = []
        zips = {}

        if self.spec.satisfies("programming_model=openmp"):
            # TODO: Support variants
            n = ["55", "110"]
            variables["n_nodes"] = ["1", "2"]
            variables["n_ranks"] = "8"
            variables["n_threads_per_proc"] = ["4", "6", "12"]
            exp_name = f"{app_name}_example_omp_{{n_nodes}}_{{n_ranks}}_{{n_threads_per_proc}}_{{px}}_{{py}}_{{pz}}_{{nx}}_{{ny}}_{{nz}}"
        elif self.spec.satisfies("programming_model=cuda"):
            # TODO: Support variants
            n = ["10", "20"]
            variables["n_gpus"] = "8"
            exp_name = f"{app_name}_example_cuda_{{n_gpus}}_{{px}}_{{py}}_{{pz}}_{{nx}}_{{ny}}_{{nz}}"
        elif self.spec.satisfies("programming_model=rocm"):
            # TODO: Support variants
            n = ["110", "220"]
            variables["n_gpus"] = "8"
            exp_name = f"{app_name}_example_rocm_{{n_gpus}}_{{px}}_{{py}}_{{pz}}_{{nx}}_{{ny}}_{{nz}}"
        else:
            raise NotImplementedError(
                "Unsupported programming_model. Only openmp, cuda and rocm are supported"
            )

        # TODO: Support variant
        p = "2"
        variables["px"] = p
        variables["py"] = p
        variables["pz"] = p

        variables["nx"] = n
        variables["ny"] = n
        variables["nz"] = n
        zips["size"] = ["nx", "ny", "nz"]

        m_tag = (
            "matrices" if self.spec.satisfies("programming_model=openmp") else "matrix"
        )
        if self.spec.satisfies("programming_model=openmp"):
            matrices.append(
                {"size_nodes_threads": ["size", "n_nodes", "n_threads_per_proc"]}
            )
        elif self.spec.satisfies("programming_model=cuda") or self.spec.satisfies(
            "programming_model=rocm"
        ):
            matrices.append("size")
        else:
            pass

        excludes = {}
        if self.spec.satisfies("programming_model=openmp"):
            excludes["where"] = [
                "{n_threads_per_proc} * {n_ranks} > {n_nodes} * {sys_cores_per_node}"
            ]

        return {
            app_name: {
                "workloads": {
                    f"{self.workload}": {
                        "experiments": {
                            exp_name: {
                                "variants": {"package_manager": "spack"},
                                "variables": variables,
                                "zips": zips,
                                "exclude": excludes,
                                m_tag: matrices,
                            }
                        }
                    }
                }
            }
        }

    def compute_modifiers_section(self):
        modifier_list = super(Amg2023, self).compute_modifiers_section()
        if not self.spec.satisfies("caliper=none"):
            for var in list(self.spec.variants["caliper"]):
                caliper_modifier_modes = {}
                caliper_modifier_modes["name"] = "caliper"
                caliper_modifier_modes["mode"] = var
                modifier_list.append(caliper_modifier_modes)
        return modifier_list

    def compute_applications_section(self):
        if self.spec.satisfies("workload=problem1"):
            self.workload = "problem1"
        else:
            self.workload = "problem2"

        if self.spec.satisfies("experiment=example"):
            return self.make_experiment_example()
        elif self.spec.satisfies("experiment=strong"):
            return self.make_experiment_strong()
        elif self.spec.satisfies("experiment=weak"):
            return self.make_experiment_weak()
        else:
            raise NotImplementedError(
                "Unsupported experiment. Only strong, weak and example experiments are supported"
            )

    def compute_spack_section(self):
        app_name = self.spec.name

        # set package versions
        app_version = "develop"
        hypre_version = "2.31.0"
        caliper_version = "master"

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

        if not self.spec.satisfies("caliper=none"):
            package_specs["caliper"] = {
                "pkg_spec": f"caliper@{caliper_version}+adiak+mpi~libunwind~libdw",
                "compiler": system_specs["compiler"],
            }
            package_specs["hypre"]["pkg_spec"] += "+caliper"
            package_specs[app_name]["pkg_spec"] += "+caliper"
            if any("topdown" in var for var in self.spec.variants["caliper"]):
                papi_support = True # check if target system supports papi
                if papi_support:
                    package_specs["caliper"]["pkg_spec"] += "+papi"
                else:
                    raise NotImplementedError(
                        "Target system does not support the papi interface"
                    )
            elif self.spec.satisfies("caliper=cuda"):
                cuda_support = self.spec.satisfies("caliper=cuda") and True # check if target system supports cuda
                if cuda_support:
                    package_specs["caliper"]["pkg_spec"] += "~papi+cuda cuda_arch={}".format(
                        system_specs["cuda_arch"]
                    )
                else:
                    raise NotImplementedError(
                        "Target system does not support the cuda interface"
                    )
            elif self.spec.satisfies("caliper=time") or self.spec.satisfies("caliper=mpi"):
                package_specs["caliper"]["pkg_spec"] += "~papi"
            
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
