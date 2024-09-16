# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from benchpark.paths import source_location


def benchpark_experiments():
    source_dir = source_location()
    experiments = []
    experiments_dir = source_dir / "experiments"
    for x in os.listdir(experiments_dir):
        for y in os.listdir(experiments_dir / x):
            experiments.append(f"{x}/{y}")
    return experiments


def benchpark_modifiers():
    source_dir = source_location()
    modifiers = []
    for x in os.listdir(source_dir / "modifiers"):
        modifiers.append(x)
    return modifiers


def benchpark_systems():
    source_dir = source_location()
    systems = []
    for x in os.listdir(source_dir / "configs"):
        if not (
            os.path.isfile(os.path.join(source_dir / "configs", x)) or x == "common"
        ):
            systems.append(x)
    return systems
