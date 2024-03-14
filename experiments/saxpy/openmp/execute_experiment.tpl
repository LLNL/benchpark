#!/bin/bash
# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

cd {experiment_run_dir}

export N_TASKS={n_ranks}
export N_NODES={n_nodes}
export GPUS_PER_NODE={gpus_per_node}
export EXPERIMENT_RUN_DIR={experiment_run_dir}

output_script=`{workload_run_dir}/../../../generate-batch`

cat <<EOF >> output_script
{command}
EOF

output_script
