# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import benchpark.paths

def test_source_location():
    assert str(benchpark.paths.source_location()).endswith("benchpark")
