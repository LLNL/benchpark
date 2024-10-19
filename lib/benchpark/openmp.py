# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0


from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.experiment import ExperimentHelperBase


class OpenMPExperiment(Experiment):
    variant(
        "openmp",
         default="non",
         values=("oui", "non"),
         description="Build and run with OpenMP",
    )

    class Helper(ExperimentHelperBase):
        def generate_spack_specs(self):
            return "+openmp" if self.spec.satisfies("openmp=oui") else "~openmp"
