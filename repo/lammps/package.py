# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *
from spack.pkg.builtin.lammps import Lammps as BuiltinLammps


class Lammps(BuiltinLammps):

  tags("nbody","large-scale","c++","python","spatial-discretization","mpi","openmp","vectorization","cuda","kokkos","rocm")

  def setup_run_environment(self, env):

    super(BuiltinLammps, self).setup_run_environment(env)

    if self.compiler.extra_rpaths:
      for rpath in self.compiler.extra_rpaths:
        env.prepend_path("LD_LIBRARY_PATH", rpath)
