# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, Tuple
import yaml  # TODO: some way to ensure yaml available

from benchpark.directives import ExperimentSystemBase
import benchpark.spec
import benchpark.paths
import benchpark.repo
import benchpark.runtime
import benchpark.variant

bootstrapper = benchpark.runtime.RuntimeResources(benchpark.paths.benchpark_home)
bootstrapper.bootstrap()

import ramble.language.language_base  # noqa
import ramble.language.language_helpers  # noqa


class Experiment(ExperimentSystemBase):
    """This is the superclass for all benchpark experiments.

    ***The Experiment class***

    Experiments are written in pure Python.

    There are two main parts of a Benchpark experiment:

      1. **The experiment class**.  Classes contain ``directives``, which are
         special functions, that add metadata (variants) to packages (see
         ``directives.py``).

      2. **Experiment instances**. Once instantiated, an experiment is
         essentially a collection of files defining an experiment in a
         Ramble workspace.
    """

    #
    # These are default values for instance variables.
    #

    # This allows analysis tools to correctly interpret the class attributes.
    variants: Dict[
        str,
        Tuple["benchpark.variant.Variant", "benchpark.spec.ConcreteExperimentSpec"],
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

    def compute_modifiers_section(self):
        # by default we use the allocation modifier and no others
        return [{"name": "allocation"}]

    def compute_applications_section(self):
        # TODO: is there some reasonable default?
        raise NotImplementedError(
            "Each experiment must implement compute_applications_section"
        )

    def compute_spack_section(self):
        # TODO: is there some reasonable default based on known variable names?
        raise NotImplementedError(
            "Each experiment must implement compute_spack_section"
        )

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
