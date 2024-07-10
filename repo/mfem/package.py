# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from spack.package import *
from spack.pkg.builtin.mfem import Mfem as BuiltinMfem


class Mfem(BuiltinMfem):
    # variant("rocm", default=False, description="Enable ROCm support")
    # depends_on("rocblas", when="+rocm")
    # depends_on("rocsolver", when="+rocm")

    requires("+rocm", when="^rocblas")
    requires("+rocm", when="^rocsolver")

    compiler_to_cpe_name = {
        "cce": "cray",
        "gcc": "gnu",
    }

    version("4.1_comm_cali", branch="comm_cali", submodules=False, git="https://github.com/gracenansamba/mfem.git")

