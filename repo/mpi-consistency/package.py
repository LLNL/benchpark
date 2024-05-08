# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *
from spack.package_base import PackageBase


class MpiConsistency(PackageBase):
    with when("+mpi%gcc"):
        for implementation in ["mvapich2", "mpich", "cray-mpich", "spectrum-mpi"]:
            for ver in [
                "8.3.1",
                "12.1.1",
            ]:
                depends_on(f"{implementation}%gcc@{ver}", when=f"%gcc@{ver} ^{implementation}")
