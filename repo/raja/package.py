# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *
from spack.pkg.builtin.raja import Raja as BuiltinRaja


class Raja(BuiltinRaja):
    version(
        "2024.02.1",
        tag="v2024.02.1",
        commit="3ada0950b0774ec907d30a9eceaf6af7478b833b",
        submodules=False,
    )
    depends_on("blt@0.6.2", type="build", when="@2024.02:")
