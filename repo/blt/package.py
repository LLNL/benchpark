# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *
from spack.pkg.builtin.blt import Blt as BuiltinBlt


class Blt(BuiltinBlt):
    version("0.6.2", sha256="84b663162957c1fe0e896ac8e94cbf2b6def4a152ccfa12a293db14fb25191c8")
