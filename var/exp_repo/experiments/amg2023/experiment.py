from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.openmp import OpenMPExperiment
from benchpark.cuda import CudaExperiment
from benchpark.rocm import ROCmExperiment
from benchpark.expr.builtin.caliper import Caliper


class Amg2023(OpenMPExperiment, CudaExperiment, ROCmExperiment, Caliper, Experiment):
    variant(
        "workload",
        default="problem1",
        values=("problem1", "problem2"),
        description="problem1 or problem2",
    )

    variant(
        "experiment",
        default="example",
        values=("strong", "weak", "example"),
        description="type of experiment",
    )

    #requires("system+papi", when(caliper=topdown*))

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

        if self.spec.satisfies("openmp=oui"):
            # TODO: Support variants
            n = ["55", "110"]
            variables["n_nodes"] = ["1", "2"]
            variables["n_ranks"] = "8"
            variables["n_threads_per_proc"] = ["4", "6", "12"]
            exp_name = f"{app_name}_example_omp_{{n_nodes}}_{{n_ranks}}_{{n_threads_per_proc}}_{{px}}_{{py}}_{{pz}}_{{nx}}_{{ny}}_{{nz}}"
        elif self.spec.satisfies("cuda=oui"):
            # TODO: Support variants
            n = ["10", "20"]
            variables["n_gpus"] = "8"
            exp_name = f"{app_name}_example_cuda_{{n_gpus}}_{{px}}_{{py}}_{{pz}}_{{nx}}_{{ny}}_{{nz}}"
        elif self.spec.satisfies("rocm=oui"):
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
            "matrices" if self.spec.satisfies("openmp=oui") else "matrix"
        )
        if self.spec.satisfies("openmp=oui"):
            matrices.append(
                {"size_nodes_threads": ["size", "n_nodes", "n_threads_per_proc"]}
            )
        elif self.spec.satisfies("cuda=oui") or self.spec.satisfies(
            "rocm=oui"
        ):
            matrices.append("size")
        else:
            pass

        excludes = {}
        if self.spec.satisfies("openmp=oui"):
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
        package_specs = super().compute_spack_section()["packages"]

        app_name = self.spec.name

        # set package versions
        app_version = "develop"
        hypre_version = "2.31.0"

        # get system config options
        # TODO: Get compiler/mpi/package handles directly from system.py
        system_specs = {}
        system_specs["compiler"] = "default-compiler"
        system_specs["mpi"] = "default-mpi"
        system_specs["lapack"] = "lapack"
        if self.spec.satisfies("cuda=oui"):
            system_specs["cuda_version"] = "{default_cuda_version}"
            system_specs["cuda_arch"] = "{cuda_arch}"
            system_specs["blas"] = "cublas-cuda"
        if self.spec.satisfies("rocm=oui"):
            system_specs["rocm_arch"] = "{rocm_arch}"
            system_specs["blas"] = "blas-rocm"

        # set package spack specs
        if self.spec.satisfies("cuda=oui"):
            package_specs[system_specs["blas"]] = (
                {}
            )  # empty package_specs value implies external package
        if self.spec.satisfies("rocm=oui"):
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

        package_specs[app_name]["pkg_spec"] += super().generate_spack_specs()

        return {
            "packages": {k: v for k, v in package_specs.items() if v},
            "environments": {
                app_name: {
                    "packages": list(package_specs.keys())
                }
            },
        }
