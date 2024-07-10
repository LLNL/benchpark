# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *


class HPCG(CMakePackage):
    """HPCG is a software package that performs a fixed number of multigrid 
    preconditioned (using a symmetric Gauss-Seidel smoother) conjugate gradient
    (PCG) iterations using double precision (64 bit) floating point values.
    """

    tags = ["benchmark"]
    homepage = "https://www.hpcg-benchmark.org/downloads/hpcg-3.1.tar.gz"
    git = "https://github.com/daboehme/hpcg.git"

    license("BSD-3")

    version("3.1", sha256="33a434e716b79e59e745f77ff72639c32623e7f928eeb7977655ffcaade0f4a4")
    version("3.1-caliper", git="https://github.com/daboehme/hpcg.git",
            branch="caliper-support", preferred=False)

    variant("mpi", default=True, description="Enable MPI support")
    variant("openmp", default=False, description="Enable OpenMP support")
    variant("caliper", default=False, description="Enable Caliper monitoring")

    depends_on("mpi", when="+mpi")
    depends_on("caliper", when="+caliper")
    depends_on("adiak", when="+caliper")

    requires("@3.1-caliper", when="+caliper")

    def cmake_args(self):
        args = [
            self.define_from_variant("HPCG_ENABLE_MPI", "mpi"),
            self.define_from_variant("HPCG_ENABLE_OPENMP", "openmp"),
            self.define_from_variant("HPCG_ENABLE_CALIPER", "caliper")
        ]

        return args

    def install(self, spec, prefix):
        # HPCG does not provide install target, so we have to copy
        # things into place.
        mkdirp(prefix.bin)
        install(join_path(self.build_directory, "xhpgc"), prefix.bin)
