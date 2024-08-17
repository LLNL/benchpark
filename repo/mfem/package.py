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

    variant("caliper", default=False, description="Build Caliper support")
    def get_make_config_options(self, spec, prefix):
        def yes_no(varstr):
            return "YES" if varstr in self.spec else "NO"
        options = super(Mfem, self).get_make_config_options(spec, prefix)
        caliper_opt = ["MFEM_USE_CALIPER=%s" % yes_no("+caliper"), ]
        return options + caliper_opt

    version("4.4_comm_cali", branch="comm_cali", submodules=False, git="https://github.com/gracenansamba/mfem.git")

    variant("caliper", default=False, description="Enable/disable Caliper support")
    depends_on("caliper", when="+caliper")
    depends_on("adiak", when="+caliper")

    def get_make_config_options(self, spec, prefix):
        def yes_no(varstr):
            return "YES" if varstr in self.spec else "NO"
        options = super(Mfem, self).get_make_config_options(spec, prefix)
        options.append("MFEM_USE_CALIPER=%s" % yes_no("+caliper"))
        if "+caliper" in self.spec: 
            options.append("CALIPER_DIR=%s" % self.spec["caliper"].prefix)
        return options
