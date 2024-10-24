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

    variant(
        "version",
        default="develop",
        description="app version",
    )

    # requires("system+papi", when(caliper=topdown*))

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
        self.add_experiment_name_prefix("example")

        if self.spec.satisfies("openmp=oui"):
            # TODO: Support variants
            n = ["55", "110"]
            self.add_experiment_variable("n_nodes", ["1", "2"], True)
            self.add_experiment_variable("n_ranks", "8", True)
            self.add_experiment_variable("n_threads_per_proc", ["4", "6", "12"], True)
        elif self.spec.satisfies("cuda=oui"):
            # TODO: Support variants
            n = ["10", "20"]
            self.add_experiment_variable("n_gpus", "8", True)
        elif self.spec.satisfies("rocm=oui"):
            # TODO: Support variants
            n = ["110", "220"]
            self.add_experiment_variable("n_gpus", "8", True)
        else:
            raise NotImplementedError(
                "Unsupported programming_model. Only openmp, cuda and rocm are supported"
            )

        # TODO: Support variant
        p = "2"
        self.add_experiment_variable("px", p, True)
        self.add_experiment_variable("py", p, True)
        self.add_experiment_variable("pz", p, True)

        self.add_experiment_variable("nx", n, True)
        self.add_experiment_variable("ny", n, True)
        self.add_experiment_variable("nz", n, True)

        self.zip_experiment_variables("size", ["nx", "ny", "nz"])

        if self.spec.satisfies("openmp=oui"):
            self.matrix_experiment_variables(["size", "n_nodes", "n_threads_per_proc"])
        if self.spec.satisfies("cuda=oui") or self.spec.satisfies("rocm=oui"):
            self.matrix_experiment_variables("size")

        if self.spec.satisfies("openmp=oui"):
            self.add_experiment_exclude(
                "{n_threads_per_proc} * {n_ranks} > {n_nodes} * {sys_cores_per_node}"
            )

    def compute_applications_section(self):
        if self.spec.satisfies("experiment=example"):
            self.make_experiment_example()
        elif self.spec.satisfies("experiment=strong"):
            self.make_experiment_strong()
        elif self.spec.satisfies("experiment=weak"):
            self.make_experiment_weak()
        else:
            raise NotImplementedError(
                "Unsupported experiment. Only strong, weak and example experiments are supported"
            )

    def compute_spack_section(self):
        # get package version
        app_version = self.spec.variants["version"][0]

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
        if self.spec.satisfies("cuda=oui") or self.spec.satisfies("rocm=oui"):
            # empty package_specs value implies external package
            self.add_spack_spec(system_specs["blas"])
        # empty package_specs value implies external package
        self.add_spack_spec(system_specs["mpi"])
        # empty package_specs value implies external package
        self.add_spack_spec(system_specs["lapack"])

        self.add_spack_spec(
            self.name, [f"amg2023@{app_version} +mpi", system_specs["compiler"]]
        )
