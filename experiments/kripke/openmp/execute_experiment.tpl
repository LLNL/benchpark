#!/bin/bash
# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

{batch_nodes}
{batch_ranks}
{batch_timeout}

cd {experiment_run_dir}

{command}
