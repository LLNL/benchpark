# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
from spack.package import Package


class ZeroModifier(Package):
    """Empty Benchpark modifier."""

    homepage = "https://example.com"
    tags = ["modifiers"]
    version('1.0.0')

    has_code = False

    def install(self, spec, prefix):
        Path(os.path.join(prefix, 'zero_modifier.txt')).touch()
