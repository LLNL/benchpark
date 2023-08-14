#!/bin/bash
{batch_nodes}
{batch_ranks}
{batch_timeout}

cd {experiment_run_dir}

{spack_setup}

{command}
