# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Dict
import yaml  # TODO: some way to ensure yaml available

from benchpark.directives import Experiment
import benchpark.spec
import benchpark.paths
import benchpark.repo
import benchpark.runtime
import benchpark.variant

bootstrapper = benchpark.runtime.RuntimeResources(benchpark.paths.benchpark_home)
bootstrapper.bootstrap()

import ramble.language.language_base  # noqa
import ramble.language.language_helpers  # noqa


class CudaExperiment(Experiment):
    """Auxiliary class which contains CUDA variant, dependencies and conflicts                                                         
    and is meant to unify and facilitate its usage.  
    """
    variant("cuda", default=False, description="Build and run with CUDA")

    #
    # These are default values for instance variables.
    #

    # This allows analysis tools to correctly interpret the class attributes.
    variants: Dict[
        "benchpark.spec.Spec",
        Dict[str, benchpark.variant.Variant],
    ]

    def __init__(self, spec):
        self.spec: "benchpark.spec.ConcreteExperimentSpec" = spec
        super().__init__()

    def compute_include_section(self):
        # include the config directory
        # TODO: does this need to change to interop with System class
        return ["./configs"]

    def compute_config_section(self):
        # default configs for all experiments
        return {
            "deprecated": True,
            "spack_flags": {"install": "--add --keep-stage", "concretize": "-U -f"},
        }

    # def compute_applications_section(self):
    #    # TODO: The default in GPU experiments is 1 MPI rank per GPU.
    #    #       What goes here?

    def compute_spack_section(self):
        # CUDA specific versions
        system_specs = {}
        system_specs["cuda_version"] = "{default_cuda_version}"
        system_specs["cuda_arch"] = "{cuda_arch}"

        package_specs = {}
        # TODO: help!!  
        # package_specs["cuda"] = needs_external(
        
        package_specs["cuda"] = {
            "pkg_spec": "cuda@{}+allow-unsupported-compilers".format(
                system_specs["cuda_version"]
            ),
        "compiler": system_specs["compiler"],
        }

        package_specs[app_name]["pkg_spec"] += "+cuda cuda_arch={}".format(
            system_specs["cuda_arch"]
        )
    
        return {
            "packages": {k: v for k, v in package_specs.items() if v},
            "environments": {app_name: {"packages": list(package_specs.keys())}},
        }

    def compute_ramble_dict(self):
        # This can be overridden by any subclass that needs more flexibility
        return {
            "ramble": {
                "include": self.compute_include_section(),
                "config": self.compute_config_section(),
                "modifiers": self.compute_modifiers_section(),
                "applications": self.compute_applications_section(),
                "software": self.compute_spack_section(),
            }
        }

    def write_ramble_dict(self, filepath):
        ramble_dict = self.compute_ramble_dict()
        with open(filepath, "w") as f:
            yaml.dump(ramble_dict, f)
