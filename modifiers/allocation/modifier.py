# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import math
from enum import Enum
from ramble.modkit import *


class AllocOpt(Enum):
    # Experiment resource requests
    N_RANKS = 1
    N_NODES = 2
    N_CORES_PER_TASK = 3
    N_THREADS = 4 # number of OMP threads per task
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
        defined[alloc_opt] = int_val

    return defined


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Allocation(BasicModifier):

    name = "allocation"

    tags("infrastructure")

    # Currently there is only one mode. The only behavior supported right
    # now is to attempt to request "enough" resources for a given
    # request (e.g. to make sure we request enough nodes, assuming we
    # know how many CPUs we want)"
    mode('standard', description='Standard execution mode for allocation')
    default_mode('standard')

    def inherit_from_application(self, app):
        super().inherit_from_application(app)

        var_defs = defined_allocation_options(app.expander)

        # Calculate unset values (e.g. determine n_nodes if not set)
        self.determine_allocation(var_defs)

        # Definitions
        for var, val in var_defs.items():
            app.define_variable(var.name.lower(), str(val))

    def determine_allocation(self, var_defs):
        v = AttrDict()
        for alloc_opt in AllocOpt:
            setattr(v, alloc_opt.name.lower(), var_defs.get(alloc_opt, None))

        if not v.n_ranks:
            if v.n_ranks_per_node and v.n_nodes:
                v.n_ranks = v.n_nodes * v.n_ranks_per_node

        if not v.n_nodes:
            if v.n_ranks:
                cpus_request_per_task = 1
                multi_cpus_per_task = n_cores_per_task or n_threads or 0
                cpus_request_per_task = max(multi_cpus_per_task, 1)
                tasks_per_node = math.floor(cpus_per_node / cpus_request_per_task)
                v.n_nodes = math.ceil(v.n_ranks / tasks_per_node)
            if v.n_gpus and v.gpus_per_node:
                v.n_nodes = math.ceil(v.n_gpus / float(v.gpus_per_node))

        if not v.n_threads:
            v.n_threads = 1

        for alloc_opt in AllocOpt:
            local_val = getattr(v, alloc_opt.name.lower(), None)
            if (alloc_opt not in var_defs) and local_val:
                var_defs[alloc_opt] = local_val
