from benchpark.directives import variant
from benchpark.experiment import Experiment


class Laghos(Experiment):

    variant(
        "experiment",
        default="example",
        values=("weak", "strong","example"),
        description="weak or strong scaling",
    )

    def compute_applications_section(self):
        variables = {}
            
        if self.spec.satisfies("experiment=weak"):
            variables["rs"] = "5"
            variables["rp"] = ["0","1","2","3"]
            variables["n_ranks"] = "8"
        elif self.spec.satisfies("experiment=strong"):
            variables["n_ranks"] = ["4","8","16","32"]
            variables["rs"] = "5"
        else:
            variables["n_nodes"] = ["1","2","4","8","16","32","64","128"]    
            variables["n_ranks"] = "{sys_cores_per_node} * {n_nodes}"
        experiment_name_template = f"laghos_{self.spec.variants['experiment'][0]}"
        experiment_name_template += "_{n_nodes}_{n_ranks}_{rs}_{rp}_{ms}"
        return {
            "laghos": {  # ramble Application name
                "workloads":{
                    # TODO replace with a hash once we have one?
                    "problem": {
                       #"variables": variables,
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
        laghos_spack_spec = "laghos@develop +metis{modifier_spack_variant}"
        zlib_spack_spec = "zlib@1.3.1 +optimize+pic+shared"
        packages = ["default-mpi", "zlib", "blas", self.spec.name, '{modifier_package_name}']

        return { 
            "packages": {
                "zlib":{
                    "pkg_spec": zlib_spack_spec,
                    "compiler": "default-compiler",
                },
                "laghos": {
                    "pkg_spec": laghos_spack_spec,
                    "compiler": "default-compiler",  # TODO: this should probably move?
                }
            },
            "environments": {"laghos": {"packages": packages}},
            
        }
