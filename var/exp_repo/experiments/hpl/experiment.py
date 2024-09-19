from benchpark.directives import variant
from benchpark.experiment import Experiment


class Hpl(Experiment):
    variant(
        "programming_model",
        default="openmp",
        values=("openmp"),
        description="on-node parallelism model",
    )

    variant(
        "workload",
        default="standard",
        description="standard",
    )

    variant(
        "experiment",
        default="example",
        values=("example"),
        description="type of experiment",
    )

    variant(
        "caliper",
        default="none",
        values=(
            "none",
            "time",
            "mpi",
            "cuda",
            "topdown-counters-all",
            "topdown-counters-toplevel",
            "topdown-all",
            "topdown-toplevel",
        ),
        description="caliper mode",
    )

    def make_experiment_example(self):
        app_name = self.spec.name

        variables = {}
        matrices = []
        zips = {}

        if self.spec.satisfies("programming_model=openmp"):
            # TODO: Support variants
            variables["N-Grids"] = "1"
            variables["Ps"] = "2"
            variables["Qs"] = "4"
            variables["N-Ns"] = "1"
            variables["Ns"] = "10000"
            variables["N-NBs"] = "1"
            variables["NBs"] = "128"

            variables["n_nodes"] = "1"
            variables["n_ranks_per_node"] = "8"
            variables["n_threads_per_proc"] = ["2", "4", "8"]
            exp_name = f"{app_name}_example_omp_{{n_nodes}}_{{n_ranks}}_{{n_threads_per_proc}}_{{Ps}}_{{Qs}}_{{Ns}}_{{NBs}}"
        else:
            raise NotImplementedError(
                "Unsupported programming_model. Only openmp is supported"
            )

        if self.spec.satisfies("programming_model=openmp"):
            matrices.append(
                ["n_threads_per_proc"]
            )

        excludes = {}
        if self.spec.satisfies("programming_model=openmp"):
            excludes["where"] = [
                "{n_threads_per_proc} * {n_ranks_per_nodes} > {sys_cores_per_node}"
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
                                "matrix": matrices,
                            }
                        }
                    }
                }
            }
        }

    def compute_modifiers_section(self):
        modifier_list = super(Hpl, self).compute_modifiers_section()
        if not self.spec.satisfies("caliper=none"):
            for var in list(self.spec.variants["caliper"]):
                caliper_modifier_modes = {}
                caliper_modifier_modes["name"] = "caliper"
                caliper_modifier_modes["mode"] = var
                modifier_list.append(caliper_modifier_modes)
        return modifier_list

    def compute_applications_section(self):
        self.workload = self.spec.variants["workload"]

        if self.spec.satisfies("experiment=example"):
            return self.make_experiment_example()
        else:
            raise NotImplementedError(
                "Unsupported experiment. Only strong, weak and example experiments are supported"
            )

    def compute_spack_section(self):
        app_name = self.spec.name

        # set package versions
        app_version = "2.3-caliper"
        caliper_version = "master"

        # get system config options
        # TODO: Get compiler/mpi/package handles directly from system.py
        system_specs = {}
        system_specs["compiler"] = "default-compiler"
        system_specs["mpi"] = "default-mpi"
        if self.spec.satisfies("programming_model=openmp"):
            system_specs["blas"] = "blas"

        # set package spack specs
        package_specs = {}
        package_specs[system_specs["blas"]] = (
            {}
        )  # empty package_specs value implies external package
        package_specs[system_specs["mpi"]] = (
            {}
        )  # empty package_specs value implies external package
        package_specs["hpl"] = {
            "pkg_spec": f"hpl@{hypre_version}",
            "compiler": system_specs["compiler"],
        }

        if not self.spec.satisfies("caliper=none"):
            package_specs["caliper"] = {
                "pkg_spec": f"caliper@{caliper_version}+adiak+mpi~libunwind~libdw",
                "compiler": system_specs["compiler"],
            }
            package_specs[app_name]["pkg_spec"] += "+caliper"
            if any("topdown" in var for var in self.spec.variants["caliper"]):
                papi_support = True  # check if target system supports papi
                if papi_support:
                    package_specs["caliper"]["pkg_spec"] += "+papi"
                else:
                    raise NotImplementedError(
                        "Target system does not support the papi interface"
                    )
            elif self.spec.satisfies("caliper=cuda"):
                cuda_support = (
                    self.spec.satisfies("caliper=cuda") and True
                )  # check if target system supports cuda
                if cuda_support:
                    package_specs["caliper"][
                        "pkg_spec"
                    ] += "~papi+cuda cuda_arch={}".format(system_specs["cuda_arch"])
                else:
                    raise NotImplementedError(
                        "Target system does not support the cuda interface"
                    )
            elif self.spec.satisfies("caliper=time") or self.spec.satisfies(
                "caliper=mpi"
            ):
                package_specs["caliper"]["pkg_spec"] += "~papi"

        if self.spec.satisfies("programming_model=openmp"):
            package_specs[app_name]["pkg_spec"] += "+openmp"

        return {
            "packages": {k: v for k, v in package_specs.items() if v},
            "environments": {app_name: {"packages": list(package_specs.keys())}},
        }
