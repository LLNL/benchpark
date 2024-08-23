from benchpark.directives import variant
from benchpark.experiment import Experiment


class OsuMicroBenchmarks(Experiment):
    #single item list causes crashes, so the variant section has been commented out for now
    #variant(
    #    "programming_model",
    #   default="mpi-only",
    #    values=("mpi-only"),
    #    description="on-node parallelism model",
    #)  
    def compute_applications_section(self):
        variables = {}
        matrix = {}
       
        variables["scaling_nodes"] = '2'
        variables["n_nodes"] = "{scaling_nodes}"
        variables["n_ranks_per_node"] = "36"

        return {
            "osu-micro-benchmarks": { 
                # TODO replace with a hash once we have one?
               "workloads": {
                  "osu_latency": {
                      "experiments": {
                          "scaling_{n_nodes}nodes_medium": {
                              "variables": variables,
                            }
                        }
                    }
                }
            }
        }

    def compute_spack_section(self):
        # TODO: express that we need certain variables from system
        # Does not need to happen before merge, separate task
        osu_microbenchmarks_spack_spec = "osu-micro-benchmarks{modifier_spack_variant}"
        packages = ["default-mpi", self.spec.name, "{modifier_package_name}"]

        return {
            "spack": {
                "packages": {
                    "osu-micro-benchmarks": {
                        "spack_spec": osu_microbenchmarks_spack_spec,
                        "compiler": "default_compiler", 
                    }
                },
                "environments": {"osu-micro-benchmarks": {"packages": packages}},
            }
        }
