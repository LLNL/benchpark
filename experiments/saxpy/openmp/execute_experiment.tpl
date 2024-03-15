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

export BATCH_SUBMIT="{batch_submit}"

export EXPERIMENT_RUN_DIR="{experiment_run_dir}"
export SETUP_AND_RUN={experiment_run_dir}/setup_and_run.txt

cat <<EOF >> "$SETUP_AND_RUN"
{command}
EOF

{workload_run_dir}/../../../generate-batch
chmod +x output_script
#output_script
