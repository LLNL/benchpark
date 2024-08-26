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

    cali_datafile = "{experiment_run_dir}/{experiment_name}.cali"

    mode(
        "time",
        description="Platform-independent collection of time",
    )

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={})".format(cali_datafile),
        method="set",
        modes=["time"],
    )

    mode(
        "mpi",
        description="Profile MPI functions",
    )

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={}, profile.mpi)".format(cali_datafile),
        method="set",
        modes=["mpi"],
    )

    mode(
        "cuda",
        description="Profile CUDA API functions",
    )

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={}, profile.cuda)".format(cali_datafile),
        method="set",
        modes=["cuda"],
    )

    mode(
        "topdown-counters-all",
        description="Raw counter values for Intel top-down analysis (all levels)",
    )

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={}, topdown-counters.all)".format(cali_datafile),
        method="set",
        modes=["topdown-counters-all"],
    )

    mode(
        "topdown-counters-toplevel",
        description="Raw counter values for Intel top-down analysis (top level)",
    )

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={}, topdown-counters.toplevel)".format(cali_datafile),
        method="set",
        modes=["topdown-counters-toplevel"],
    )

    mode(
        "topdown-all",
        description="Top-down analysis for Intel CPUs (all levels)",
    )

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={}, topdown.all)".format(cali_datafile),
        method="set",
        modes=["topdown-all"],
    )

    mode(
        "topdown-toplevel",
        description="Top-down analysis for Intel CPUs (top level)",
    )

    env_var_modification(
        "CALI_CONFIG",
        "spot(output={}, topdown.toplevel)".format(cali_datafile),
        method="set",
        modes=["topdown-toplevel"],
    )

    archive_pattern(cali_datafile)

    software_spec("caliper", pkg_spec="caliper")

    required_package("caliper")
