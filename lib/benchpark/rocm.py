# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0


from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.experiment import ExperimentHelperBase


class ROCmExperiment:
    variant(
        "rocm",
         default="non",
         values=("oui", "non"),
         description="Build and run with ROCm",
    )

    class Helper(ExperimentHelperBase):
        def generate_spack_specs(self):
            return "+rocm" if self.spec.satisfies("+rocm") else "~rocm"
