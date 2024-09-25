from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.expr.builtin.scaling import Scaling


class Kripke(Scaling, Experiment):
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
        n_ranks = "{npx}*{npy}*{npz}"
        n_threads_per_proc = "1"

        # Number of zones in each dimension, per process
        initial_nzx = 64
        initial_nzy = 64
        initial_nzz = 32

        # Number of processes in each dimension
        initial_npx = 2
        initial_npy = 2
        initial_npz = 1

        if self.spec.satisfies("scaling=single-node"):
            nzx = str(initial_nzx)
            nzy = str(initial_nzy)
            nzz = str(initial_nzz)

            npx = str(initial_npx)
            npy = str(initial_npy)
            npz = str(initial_npz)

        if self.spec.satisfies("scaling=strong" or "scaling=weak"):
            nzx = str(initial_nzx)
            nzy = str(initial_nzy)
            nzz = str(initial_nzz)

            # Number of processes in each dimension
            np_list = self.generate_strong_scaling_parameters([initial_npx, initial_npy, initial_npz])
            npx = np_list[0]
            npy = np_list[1]
            npz = np_list[2]
        if self.spec.satisfies("scaling=weak"):
            # Number of zones in each dimension
            nzx = [str(initial_nzx)]
            nzy = [str(initial_nzy)]
            nzz = [str(initial_nzz)]
            for i in (3, 4, 5):  # doubles in round robin
                if i % 3 == 0:
                    initial_nzz *= 2
                if i % 3 == 1:
                    initial_nzx *= 2
                if i % 3 == 2:
                    initial_nzy *= 2
                npx.append(str(initial_npx))
                npy.append(str(initial_npy))
                npz.append(str(initial_npz))

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
