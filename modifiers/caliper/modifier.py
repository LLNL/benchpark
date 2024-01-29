# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from ramble.modkit import *


class Caliper(SpackModifier):
    """Define a modifier for Caliper"""

    name = "caliper"

    tags("profiler", "performance-analysis")

    maintainers("pearce8")

    mode("time", description="Platform-independent collection of time")

    _cali_datafile = "{experiment_run_dir}/{experiment_name}.cali"

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={})".format(_cali_datafile),
        method="set",
        modes=["time"],
    )

    archive_pattern(_cali_datafile)

    software_spec("caliper", spack_spec="caliper")

    required_package("caliper")
