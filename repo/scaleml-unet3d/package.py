# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *


class UnetBenchmarkGit(Package):
    """TO_BE_NAMED is a scalable machine learning benchmark for 3d semantic segmentation."""

    tags = ["benchmark"]
    homepage = "http://example.com"
    git = "https://lc.llnl.gov/gitlab/hao3/unet-benchmark.git"

    license("UNKNOWN", checked_by="Thionazin")

    version("main", sha256="332afea93d2520963437da808108beb814fb98ac78df12d693b2a37b61815d21")

    depends_on("anaconda3", type=("build", "run"))

    def install(self, spec, prefix):
        bash = which("bash")
        bash("conda", "env", "create", "-f", join_path(self.build_directory, "requirements.yaml"))

