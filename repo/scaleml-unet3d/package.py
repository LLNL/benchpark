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

    depends_on("python@3.10", type=("build", "run"))
    depends_on("py-mpi4py", type=("build", "run"))
    depends_on("py-torch", type=("build", "run"))
    depends_on("py-torchvision", type=("build", "run"))
    depends_on("py-matplotlib", type=("build", "run"))
    depends_on("py-numpy@1.23.0", type=("build", "run"))
    depends_on("py-pillow", type=("build", "run"))
    depends_on("py-tqdm", type=("build", "run"))
    depends_on("py-wandb", type=("build", "run"))
    depends_on("py-open3d+python", type=("build", "run"))
    # Add pyntcloud, may have to integrate
    depends_on("py-pyyaml", type=("build", "run"))

