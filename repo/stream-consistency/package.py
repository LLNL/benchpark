# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *
from spack.package_base import PackageBase


class StreamConsistency(PackageBase):
    with when("+mpi%gcc"):
        for ver in [
            "12.1.1",
        ]:
            depends_on(f"mpi%gcc@{ver}", when=f"%gcc@{ver}")
