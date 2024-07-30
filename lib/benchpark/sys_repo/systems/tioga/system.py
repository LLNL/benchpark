# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib

from benchpark.system import System


class Tioga(System):
    def __init__(self):
        super().__init__()

        self.scheduler = "flux"
        self.sys_cores_per_node = "64"
        self.sys_gpus_per_node = "4"

        self.external_resources = pathlib.Path(Tioga.resource_location) / "externals"
