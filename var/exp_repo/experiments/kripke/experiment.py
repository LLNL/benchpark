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
            self.add_experiment_name_prefix("single_node")
            nzx = initial_nzx
            nzy = initial_nzy
            nzz = initial_nzz

            npx = initial_npx
            npy = initial_npy
            npz = initial_npz

        if self.spec.satisfies("scaling=strong"):
            self.add_experiment_name_prefix("strong")
            nzx = initial_nzx
            nzy = initial_nzy
            nzz = initial_nzz

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
            self.add_experiment_name_prefix("weak")
            # Number of zones in each dimension
            npx = [initial_npx]
            npy = [initial_npy]
            npz = [initial_npz]
            nzx = [initial_nzx]
            nzy = [initial_nzy]
            nzz = [initial_nzz]
            for i in (3, 4, 5):  # doubles in round robin
                if i % 3 == 0:
                    initial_npz *= 2
                    initial_nzz *= 2
                if i % 3 == 1:
                    initial_npx *= 2
                    initial_nzx *= 2
                if i % 3 == 2:
                    initial_npy *= 2
                    initial_nzy *= 2
                npx.append(initial_npx)
                npy.append(initial_npy)
                npz.append(initial_npz)
                nzx.append(initial_nzx)
                nzy.append(initial_nzy)
                nzz.append(initial_nzz)

        self.add_experiment_variable("experiment_setup", "")
        self.add_experiment_variable("n_ranks", n_ranks, True)
        self.add_experiment_variable("n_threads_per_proc", n_threads_per_proc, True)
        self.add_experiment_variable("ngroups", 64, True)
        self.add_experiment_variable("gs", 1, True)
        self.add_experiment_variable("nquad", 128, True)
        self.add_experiment_variable("ds", 128, True)
        self.add_experiment_variable("lorder", 4, True)
        self.add_experiment_variable("nzx", nzx, True)
        self.add_experiment_variable("nzy", nzy, True)
        self.add_experiment_variable("nzz", nzz, True)
        self.add_experiment_variable("npx", npx, True)
        self.add_experiment_variable("npy", npy, True)
        self.add_experiment_variable("npz", npz, True)

        if self.spec.satisfies("openmp=oui"):
            self.add_experiment_variable("arch", "OpenMP")
        elif self.spec.satisfies("cuda=oui"):
            self.add_experiment_variable("arch", "CUDA")
        elif self.spec.satisfies("rocm=oui"):
            self.add_experiment_variable("arch", "HIP")

        elif self.spec.satisfies("cuda=oui") or self.spec.satisfies("rocm=oui"):
            self.add_experiment_variable("n_gpus", n_ranks)

    def compute_spack_section(self):
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
        # empty package_specs value implies external package
        self.add_spack_spec(system_specs["mpi"])

        self.add_spack_spec(
            self.name, [f"kripke@{app_version} +mpi", system_specs["compiler"]]
        )
