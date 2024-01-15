# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *
from ramble.app.builtin.lammps import Lammps as LammpsBase


class Lammps(LammpsBase):

    tags = ['asc','chemistry','material-science','molecular-dynamics',
            'fft','particles',
            'large-scale','multi-node','single-node','sub-node',
            'mpi','network-collectives','network-point-to-point',
            'c++','kokkos','fortran','openmp']
