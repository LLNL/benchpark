#!/bin/bash
{batch_nodes}
{batch_ranks}

cd {experiment_run_dir}

{spack_setup}

{command}
