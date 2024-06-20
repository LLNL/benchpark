# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *


class Amg2023(CMakePackage, CudaPackage, ROCmPackage):
    """AMG2023 is a parallel algebraic multigrid solver for linear systems
    arising from problems on unstructured grids. The driver provided here
    builds linear systems for various 3-dimensional problems. It requires
    an installation of hypre-2.31.0 or higher.
    """

    tags = ["benchmark"]
    homepage = "https://github.com/LLNL/AMG2023"
    git = "https://github.com/LLNL/AMG2023.git"
    git = "https://github.com/gracenansamba/hypre.git"

    license("Apache-2.0")

    version("develop", branch="main")
    version("comm_cali", branch="comm_cali")

    variant("mpi", default=True, description="Enable MPI support")
    variant("openmp", default=False, description="Enable OpenMP support")
    variant("caliper", default=False, description="Enable Caliper monitoring")

    depends_on("mpi", when="+mpi")
    depends_on("hypre+mpi", when="+mpi")
    requires("+mpi", when="^hypre+mpi")
    depends_on("caliper", when="+caliper")
    depends_on("adiak", when="+caliper")
    depends_on("hypre+caliper", when="+caliper")
    # depends_on("hypre@2.31.0:")
    depends_on("hypre@comm_cali:")
    depends_on("hypre+cuda", when="+cuda")
    requires("+cuda", when="^hypre+cuda")
    depends_on("hypre+rocm", when="+rocm")
    requires("+rocm", when="^hypre+rocm")

    def cmake_args(self):
        cmake_options = []
        cmake_options.append(self.define_from_variant("AMG_WITH_CALIPER", "caliper"))
        cmake_options.append(self.define_from_variant("AMG_WITH_OMP", "openmp"))
        cmake_options.append(self.define("HYPRE_PREFIX", self.spec["hypre"].prefix))
        if self.spec["hypre"].satisfies("+cuda"):
            cmake_options.append("-DAMG_WITH_CUDA=ON")
        if self.spec["hypre"].satisfies("+rocm"):
            cmake_options.append("-DAMG_WITH_HIP=ON")
        if self.spec["hypre"].satisfies("+mpi"):
            cmake_options.append("-DAMG_WITH_MPI=ON")

        return cmake_options
