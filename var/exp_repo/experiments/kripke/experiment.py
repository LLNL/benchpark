from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.expr.builtin.scalingexperiment import ScalingExperiment


class Kripke(ScalingExperiment, Experiment):
    variant(
        "programming_model",
        default="openmp",
        values=("openmp", "cuda", "rocm"),
        description="node-level parallelism model",
    )

    variant(
        "scaling",
        default="single-node",
        values=("single-node", "weak", "strong"),
        description="Single node, weak scaling, or strong scaling study",
    )

    def compute_applications_section(self):
        n_ranks = "{npx} * {npy} * {npz}"
        n_threads_per_proc = 1

        # Number of processes in each dimension
        initial_np = [2, 2, 1]

        # Number of zones in each dimension, per process
        initial_nz = [64, 64, 32]

        if self.spec.satisfies("scaling=single-node"):
            npx = initial_np[0]
            npy = initial_np[1]
            npz = initial_np[2]

            nzx = initial_nz[0]
            nzy = initial_nz[1]
            nzz = initial_nz[2]
        else:
            input_params = {}
            if self.spec.satisfies("scaling=strong") or self.spec.satisfies("scaling=weak"):
                input_params["np"] = initial_np
            if self.spec.satisfies("scaling=weak"):
                input_params["nz"] = initial_nz
            scaled_params = self.scale_experiment_variables(input_params, "np")
            npx = scaled_params["np"][0]
            npy = scaled_params["np"][1]
            npz = scaled_params["np"][2]

            nzx = scaled_params["nz"][0]
            nzy = scaled_params["nz"][1]
            nzz = scaled_params["nz"][2]

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
        elif self.spec.satisfies("programming_model=cuda"):
            variables["arch"] = "CUDA"
            variables["n_gpus"] = n_ranks
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
        kripke_spec = "kripke@develop+mpi"
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
                    "compiler": "default-compiler",
                }
            },
            "environments": {
                "kripke": {
                    "packages": [
                        "default-mpi",
                        "kripke",
                    ]
                }
            },
        }
