from benchpark.directives import variant
from benchpark.experiment import Experiment


class Saxpy(Experiment):
    variant(
        "programming_model",
        default="openmp",
        values=("openmp", "cuda", "rocm"),
        description="on-node parallelism model",
    )

    def compute_applications_section(self):
        variables = {}
        matrix = {}

        # GPU tests include some smaller sizes
        n = ["512", "1024"]
        matrix = ["n"]
        if self.spec.satisfies("programming_model=openmp"):
            matrix += ["omp_num_threads"]
            variables["n_nodes"] = ["1", "2"]
            variables["n_ranks"] = "8"
            variables["omp_num_threads"] = ["2", "4"]
        else:
            n = ["128", "256"] + n
            variables["n_gpus"] = "1"

        variables["n"] = n

        return {
            "saxpy": {  # ramble Application name
                "workloads": {
                    # TODO replace with a hash once we have one?
                    "problem": {
                        "experiments": {
                            "saxpy_{n}_{n_nodes}_{omp_num_threads}": {
                                "variables": variables,
                                "matrices": matrix,
                            }
                        }
                    }
                }
            }
        }

    def compute_spack_section(self):
        # TODO: express that we need certain variables from system
        # Does not need to happen before merge, separate task
        saxpy_spack_spec = "saxpy@1.0.0{modifier_spack_variant}"
        if self.spec.satisfies("programming_model=openmp"):
            saxpy_spack_spec += "+openmp"
        elif self.spec.satisfies("programming_model=cuda"):
            saxpy_spack_spec += "+cuda cuda_arch={cuda_arch}"
        elif self.spec.satisfies("programming_model=rocm"):
            saxpy_spack_spec += "+rocm amdgpu_target={rocm_arch}"

        packages = ["default-mpi", self.spec.name, "{modifier_package_name}"]

        return {
            "spack": {
                "packages": {
                    "saxpy": {
                        "spack_spec": saxpy_spack_spec,
                        "compiler": "default_compiler",  # TODO: this should probably move?
                    }
                },
                "environments": {"saxpy": {"packages": packages}},
            }
        }
