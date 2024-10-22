from benchpark.directives import variant
from benchpark.experiment import Experiment


class Laghos(Experiment):

    variant(
        "experiment",
        default="strong",
        values=("single-node", "strong"),
        description="weak or strong scaling",
    )

    variant(
        "workload",
        default="triplept",
        description="triplept or other problem",
    )

    def compute_applications_section(self):
        app_name = self.spec.name
        if self.spec.satisfies("workload=triplept"):
            self.workload = "triplept"
        else:
            self.workload = "triplept"
        variables = {}

        if self.spec.satisfies("experiment=single-node"):
            variables["n_nodes"] = ["1"]
        elif self.spec.satisfies("experiment=strong"):
            variables["n_nodes"] = ["1", "2", "4", "8", "16", "32", "64", "128"]

        variables["n_ranks"] = "{sys_cores_per_node} * {n_nodes}"

        experiment_name_template = f"laghos_{self.spec.variants['experiment'][0]}"
        experiment_name_template += "_{n_nodes}_{n_ranks}"
        return {
            app_name: {  # ramble Application name
                "workloads": {
                    f"{self.workload}": {
                        "experiments": {
                            experiment_name_template: {
                                "variants": {"package_manager": "spack"},
                                "variables": variables,
                            }
                        }
                    }
                }
            }
        }

    def compute_spack_section(self):
        laghos_spack_spec = "laghos@develop +metis"
        zlib_spack_spec = "zlib@1.3.1 +optimize+pic+shared"
        packages = [
            "default-mpi",
            "zlib",
            "blas",
            self.spec.name,
        ]

        return {
            "packages": {
                "zlib": {
                    "pkg_spec": zlib_spack_spec,
                    "compiler": "default-compiler",
                },
                "laghos": {
                    "pkg_spec": laghos_spack_spec,
                    "compiler": "default-compiler",  # TODO: this should probably move?
                },
            },
            "environments": {"laghos": {"packages": packages}},
        }
