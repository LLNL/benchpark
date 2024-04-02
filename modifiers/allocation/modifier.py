# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import math

from ramble.modkit import *


class AllocOpt(Enum):
    # Experiment resource requests
    N_RANKS = 1
    N_NODES = 2
    N_CORES_PER_TASK = 3
    N_OMP_THREADS_PER_TASK = 4
    N_RANKS_PER_NODE = 5

    # Descriptions of resources available on systems
    GPUS_PER_NODE = 100
    CPUS_PER_NODE = 101


# If we see this value, we assume the user wants us to substitute it.
# Ramble expects n_ranks and n_nodes to be set.
SENTINEL_UNDEFINED_VALUE = 7


def defined_allocation_options(expander):
    """For each possible allocation option, check if it was filled in by
       Ramble: in that case it will be an integer.
    """
    defined = {}
    for alloc_opt in AllocOpt:
        var_def = expander.expand_var(f"{{{alloc_opt.name.lower()}}}")
        try:
            int_val = int(var_def)
        except ValueError:
            continue
        if int_val == SENTINEL_UNDEFINED_VALUE:
            continue
        defined[alloc_opt] = var_def

    return defined


class Allocation(BaseModifier):

    name = "allocation"

    tags("infrastructure")

    def inherit_from_application(self, app):
        super().inherit_from_application(app)

        var_defs = defined_allocation_options(self.expander)

        # Calculate unset values (e.g. determine n_nodes if not set)
        determine_allocation(var_defs)

        # Definitions
        for var, val in var_defs.items():
            app.define_variable(var.name.lower(), val)


    def determine_allocation(var_defs):
        # Define e.g. "n_ranks" as local variables based on what is currently
        # defined in Ramble configs
        for alloc_opt in AllocOpt:
            locals()[alloc_opt.name.lower()] = var_defs.get(alloc_opt, None)

        if not n_ranks:
            if n_ranks_per_node and n_nodes:
                n_ranks = n_nodes * n_ranks_per_node

        if not n_nodes:
            if n_ranks:
                cpus_request_per_task = 1
                multi_cpus_per_task = n_cores_per_task or n_omp_threads_per_task or 0
                cpus_request_per_task = max(multi_cpus_per_task, 1)
                tasks_per_node = math.floor(cpus_per_node / cpus_request_per_task)
                n_nodes = math.ceil(n_ranks / tasks_per_node)
            if n_gpus and gpus_per_node:
                n_nodes = math.ceil(n_gpus / float(gpus_per_node))

        for alloc_opt in AllocOpt:
            local_val = locals()[alloc_opt.name.lower()]
            if (alloc_opt not in var_defs) and local_val:
                var_defs[alloc_opt] = local_val
