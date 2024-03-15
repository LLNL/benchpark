#!/bin/bash
# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

cd {experiment_run_dir}

export N_TASKS="{n_ranks}"
export N_NODES="{n_nodes}"
export GPUS_PER_NODE="{gpus_per_node}"
export CORES_PER_TASK="{cores_per_task}"

export SCHEDULER="{scheduler}"

export EXPERIMENT_RUN_DIR="{experiment_run_dir}"
export SETUP_AND_RUN={experiment_run_dir}/setup_and_run.txt

echo "step 1"

cat <<EOF >> "$SETUP_AND_RUN"
{command}
EOF

echo "step 2"

result=`{workload_run_dir}/../../../generate-batch`
read invoke_with output_script <<< "$result"

echo "step 3"

chmod +x "$output_script"
#"$invoke_with" "$output_script"
