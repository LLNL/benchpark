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

    def compute_include_section(self):
        return [
            "./configs/software.yaml",
            "./configs/variables.yaml",
            "./configs/modifier.yaml",
        ]

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

        app_spack_spec = "amg2023@develop +mpi{modifier_spack_variant}"
        hypre_spack_spec = "hypre@2.31.0 +mpi+mixedint~fortran{modifier_spack_variant}"

        # TODO: Handle compiler handles through system.py
        compiler = "default-compiler"

        package_specs = {}
        # TODO: Handle package handles through system.py
        packages = [
            "default-mpi",
            "lapack",
            "hypre",
            app_name,
            "{modifier_package_name}",
        ]

        if self.spec.satisfies("programming_model=openmp"):
            app_spack_spec += "+openmp"
            hypre_spack_spec += "+openmp"
        elif self.spec.satisfies("programming_model=cuda"):
            app_spack_spec += "+cuda cuda_arch={cuda_arch}"
            hypre_spack_spec += "+cuda cuda_arch={cuda_arch}"
            # TODO: Handle package handles through system.py
            packages = ["cuda", "cublas-cuda"] + packages
            cuda_spack_spec = "cuda@{default_cuda_version}+allow-unsupported-compilers"
            package_specs["cuda"] = {
                "pkg_spec": cuda_spack_spec,
                "compiler": compiler,
            }

        elif self.spec.satisfies("programming_model=rocm"):
            app_spack_spec += "+rocm amdgpu_target={rocm_arch}"
            hypre_spack_spec += "+rocm amdgpu_target={rocm_arch}"
            # TODO: Handle package handles through system.py
            packages = ["blas-rocm"] + packages

        package_specs["hypre"] = {
            "pkg_spec": hypre_spack_spec,
            "compiler": compiler,
        }

        package_specs[app_name] = {
            "pkg_spec": app_spack_spec,
            "compiler": compiler,
        }

        return {
            "packages": package_specs,
            "environments": {app_name: {"packages": packages}},
        }

    def compute_ramble_dict(self):
        ramble_dict = super(Amg2023, self).compute_ramble_dict()
        ramble_dict["ramble"]["software"] = ramble_dict["ramble"].pop("spack")
        return ramble_dict
