# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Amg2023(MakefilePackage, CudaPackage, ROCmPackage):
    """AMG2023 is a parallel algebraic multigrid solver for linear systems
       arising from problems on unstructured grids. The driver provided here
       builds linear systems for various 3-dimensional problems. It requires
       an installation of hypre-2.27.0 or higher.
    """

    tags = ["benchmark"]
    homepage = "https://github.com/LLNL/AMG2023"
    git = "https://github.com/LLNL/AMG2023.git"

    version("develop", branch="main")

    variant("mpi", default=True, description="Enable MPI support")
    variant("openmp", default=False, description="Enable OpenMP support")

    depends_on("hypre@2.27.0:")
    depends_on("mpi", when="+mpi")

    def edit(self, spec, prefix):
        makefile = FileFilter('Makefile')
        if "+mpi" in spec:
            makefile.filter('CC        = .*', 'CC        = {0}'.format(spec["mpi"].mpicc))
            makefile.filter('CXX       = .*', 'CXX       = {0}'.format(spec["mpi"].mpicxx))
        else:
            makefile.filter('CC        = .*', 'CC        = {0}'.format(spack_cc))
            makefile.filter('CXX       = .*', 'CXX       = {0}'.format(spack_cc))

        makefile.filter('HYPRE_DIR = .*', 'HYPRE_DIR = {0}'.format(self.spec['hypre'].prefix))

        if "+cuda" in spec:
            makefile.filter('HYPRE_CUDA_PATH    = .*', 'HYPRE_CUDA_PATH    = %s' % (spec["cuda"].prefix))
            makefile.filter('HYPRE_CUDA_INCLUDE = #', 'HYPRE_CUDA_INCLUDE = ')
            makefile.filter('HYPRE_CUDA_LIBS    = #', 'HYPRE_CUDA_LIBS    = ')
            makefile.filter('HYPRE_HIP_PATH    =', '#HYPRE_HIP_PATH    =')
            makefile.filter('HYPRE_HIP_INCLUDE =', '#HYPRE_HIP_INCLUDE =')
            makefile.filter('HYPRE_HIP_LIBS    =', '#HYPRE_HIP_LIBS    =')

        if "+rocm" in spec:
            makefile.filter('HYPRE_HIP_PATH    = .*', f'HYPRE_HIP_PATH    = {spec["hip"].prefix}')
        else:
            makefile.filter('HYPRE_HIP_PATH    =', '#HYPRE_HIP_PATH    =')
            makefile.filter('HYPRE_HIP_INCLUDE =', '#HYPRE_HIP_INCLUDE =')
            makefile.filter('HYPRE_HIP_LIBS    =', '#HYPRE_HIP_LIBS    =')

        if "+mpi" in spec:
            makefile.filter('#MPIPATH = .*', 'MPIPATH = {0}'.format(spec["mpi"].prefix))
            makefile.filter('#MPIINCLUDE', 'MPIINCLUDE')
            if spec["mpi"].extra_attributes and "ldflags" in spec["mpi"].extra_attributes:
               makefile.filter('#MPILIBS    = .*', 'MPILIBS    = {0}'.format(spec["mpi"].extra_attributes["ldflags"]))
            else:
               makefile.filter('#MPILIBDIRS', 'MPILIBDIRS')
               makefile.filter('#MPILIBS', 'MPILIBS')
            makefile.filter('#MPIFLAGS', 'MPIFLAGS')

    def install(self, spec, prefix):
        make()
        mkdirp(prefix.bin)
        install("amg", prefix.bin)
