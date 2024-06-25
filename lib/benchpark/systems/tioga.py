# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import pathlib

from .base import System


class Tioga(System):
    def __init__(self):
        super().__init__()

        self.scheduler = "flux"
        self.sys_cores_per_node = "64"
        self.sys_gpus_per_node = "4"

        base = pathlib.Path(os.path.abspath(__module__.__file__)).parents[0] 
        self.external_resources = base / "externals" / "tioga"

