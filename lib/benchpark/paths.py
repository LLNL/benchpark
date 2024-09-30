# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib

benchpark_home = pathlib.Path(os.path.expanduser("~/.benchpark"))
global_ramble_path = benchpark_home / "ramble"
global_spack_path = benchpark_home / "spack"


def source_location():
    the_directory_with_this_file = os.path.dirname(os.path.abspath(__file__))
    return pathlib.Path(the_directory_with_this_file).parent.parent


benchpark_root = source_location()
