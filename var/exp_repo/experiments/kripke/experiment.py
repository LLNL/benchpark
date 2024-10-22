from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.openmp import OpenMPExperiment
from benchpark.cuda import CudaExperiment
from benchpark.rocm import ROCmExperiment


class Kripke(OpenMPExperiment, CudaExperiment, ROCmExperiment, Experiment):
    variant(
        "scaling",
        default="single-node",
        values=("single-node", "weak", "strong"),
        description="Single node, weak scaling, or strong scaling study",
    )

    variant(
        "version",
        default="develop",
        description="app version",
    )

    variant(
        "extra_specs",
        default=" ",
        description="custom spack specs",
    )

    def compute_applications_section(self):
        n_ranks = "{npx} * {npy} * {npz}"
        n_threads_per_proc = 1

        # Number of zones in each dimension, per process
        initial_nzx = 64
        initial_nzy = 64
        initial_nzz = 32

        # Number of processes in each dimension
        initial_npx = 2
        initial_npy = 2
        initial_npz = 1

        if self.spec.satisfies("scaling=single-node"):
            nzx = initial_nzx
            nzy = initial_nzy
            nzz = initial_nzz

            npx = initial_npx
            npy = initial_npy
            npz = initial_npz

        if self.spec.satisfies("scaling=strong"):
            # Number of processes in each dimension
            npx = [initial_npx]
            npy = [initial_npy]
            npz = [initial_npz]
            for i in (3, 4, 5):  # doubles in round robin
                if i % 3 == 0:
                    initial_npz *= 2
                if i % 3 == 1:
                    initial_npx *= 2
                if i % 3 == 2:
                    initial_npy *= 2
                npx.append(initial_npx)
                npy.append(initial_npy)
                npz.append(initial_npz)

        if self.spec.satisfies("scaling=weak"):
            # Number of zones in each dimension
            npx = [initial_npx]
            npy = [initial_npy]
            npz = [initial_npz]
            nzx = [initial_nzx]
            nzy = [initial_nzy]
            nzz = [initial_nzz]
            for i in (3, 4, 5):  # doubles in round robin
                if i % 3 == 0:
                    initial_nzz *= 2
                if i % 3 == 1:
                    initial_nzx *= 2
                if i % 3 == 2:
                    initial_nzy *= 2
                npx.append(initial_npx)
                npy.append(initial_npy)
                npz.append(initial_npz)

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

        if self.spec.satisfies("openmp=oui"):
            variables["arch"] = "OpenMP"
            variables["omp_num_threads"] = n_threads_per_proc
        elif self.spec.satisfies("cuda=oui"):
            variables["arch"] = "CUDA"
            variables["n_gpus"] = n_ranks
        elif self.spec.satisfies("rocm=oui"):
            variables["arch"] = "HIP"

        experiment_name_template = (
            f"kripke_{variables['arch']}_{self.spec.variants['scaling'][0]}"
        )
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
        package_specs = super().compute_spack_section()["packages"]

        app_name = self.spec.name

        # set package versions
        app_version = self.spec.variants["version"][0]

        # get system config options
        # TODO: Get compiler/mpi/package handles directly from system.py
        system_specs = {}
        system_specs["compiler"] = "default-compiler"
        system_specs["mpi"] = "default-mpi"
        if self.spec.satisfies("cuda=oui"):
            system_specs["cuda_version"] = "{default_cuda_version}"
            system_specs["cuda_arch"] = "{cuda_arch}"
        if self.spec.satisfies("rocm=oui"):
            system_specs["rocm_arch"] = "{rocm_arch}"

        # set package spack specs
        package_specs[system_specs["mpi"]] = (
            {}
        )  # empty package_specs value implies external package
        package_specs[app_name] = {
            "pkg_spec": f"kripke@{app_version} +mpi",
            "compiler": system_specs["compiler"],
        }

        package_specs[app_name]["pkg_spec"] += super().generate_spack_specs()
        package_specs[app_name]["pkg_spec"] += (
            " " + self.spec.variants["extra_specs"][0]
        )
        package_specs[app_name]["pkg_spec"] = package_specs[app_name][
            "pkg_spec"
        ].strip()

        return {
            "packages": {k: v for k, v in package_specs.items() if v},
            "environments": {app_name: {"packages": list(package_specs.keys())}},
        }
