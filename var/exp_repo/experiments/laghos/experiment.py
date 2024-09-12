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
            
        if self.spec.satisfies("scaling=weak"):
            variables["rs"] = ["5","6"]
            variables["n_nodes"] = ["1","8"]
        elif self.spec.satisfies("scaling=strong"):
            variables["n_nodes"] = ["1","8"]
            variables["rs"] = "5"
        else:
            variables["n_nodes"] = ["1","2","4","8","16","32","64","128"]    
        variables["n_ranks"] = "{sys_cores_per_node} * {n_nodes}"

        return {
            "laghos": {  # ramble Application name
                "workloads":{
                    # TODO replace with a hash once we have one?
                    "problem": {
                       #"variables": variables,
                        "experiments": {
                            "laghos_{n_nodes}_{n_ranks}": {
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
