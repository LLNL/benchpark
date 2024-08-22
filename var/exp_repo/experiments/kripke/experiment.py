from benchpark.directives import variant
from benchpark.experiment import Experiment


class Kripke(Experiment):
    variant(
        "programming_model",
        default="openmp",
        values=("openmp", "cuda", "rocm"),
        description="node-level parallelism model",
    )

    variant(
        "scaling",
        default="weak",
        values=("weak", "strong"),
        description="weak or strong scaling study",
    )

    def compute_applications_section(self):
        n_ranks = "{npx}*{npy}*{npz}"
        n_threads_per_proc = "1"

        npx = ["2", "2", "4", "4"]
        npy = ["2", "2", "2", "4"]
        npz = ["1", "2", "2", "2"]

        nzx = "64"
        nzy = "64"
        nzz = "32"
        if self.spec.satisfies("scaling=weak"):
            nzx = ["64", "64", "128", "128"]
            nzy = ["64", "64", "64", "128"]
            nzz = ["32", "64", "64", "64"]

        variables = {
            "experiment_setup": "",
            "n_ranks": n_ranks,
            "n_threads_per_proc": n_threads_per_proc,
            "ngroups": 64,
            "gs": 1,
            "nquad": 128,
            "ds": 128,
            "lorder": 4,
            "nzx": nzx,
            "nzy": nzy,
            "nzz": nzz,
            "npx": npx,
            "npy": npy,
            "npz": npz,
        }

        if self.spec.satisfies("programming_model=openmp"):
            variables["arch"] = "OpenMP"
            variables["omp_num_threads"] = "{n_threads_per_proc}"
        elif self.spec.satisfies("programming_model=cuda"):
            variables["arch"] = "CUDA"
            variables["n_gpus"] = "{n_ranks}"
        elif self.spec.satisfies("programming_model=rocm"):
            variables["arch"] = "HIP"

        experiment_name_template = f"kripke_{self.spec.variants['programming_model'][0]}_{self.spec.variants['scaling'][0]}"
        experiment_name_template += "_{n_nodes}_{n_ranks}_{n_threads_per_proc}_{ngroups}_{gs}_{nquad}_{ds}_{lorder}_{nzx}_{nzy}_{nzz}_{npx}_{npy}_{npz}"

        return {
            "kripke": {
                "workloads": {
                    "kripke": {
                        "experiments": {
                            experiment_name_template: {
                                "variants": {
                                    "package_manager": "spack",
                                },
                                "variables": variables,
                            }
                        }
                    }
                }
            }
        }

    def compute_spack_section(self):
        kripke_spec = "kripke@develop+mpi{modifier_spack_variant}"
        if self.spec.satisfies("programming_model=openmp"):
            pass
        elif self.spec.satisfies("programming_model=cuda"):
            pass
        elif self.spec.satisfies("programming_model=rocm"):
            kripke_spec += "+rocm"
        kripke_spec += "^chai@2024.02"

        return {
            "packages": {
                "kripke": {
                    "pkg_spec": kripke_spec,
                    "compiler": "default_compiler",
                }
            },
            "environments": {
                "kripke": {
                    "packages": [
                        "default_mpi",
                        "kripke",
                        "{modifier_package_name}",
                    ]
                }
            },
        }
