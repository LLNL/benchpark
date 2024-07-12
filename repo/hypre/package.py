# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from spack.package import *
from spack.pkg.builtin.hypre import Hypre as BuiltinHypre


class Hypre(BuiltinHypre):
    requires("+rocm", when="^rocblas")
    requires("+rocm", when="^rocsolver")

    compiler_to_cpe_name = {
        "cce": "cray",
        "gcc": "gnu",
    }

    version("2.31_comm_cali", branch="comm_cali", submodules=False, git="https://github.com/gracenansamba/hypre.git")

