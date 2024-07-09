# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *
from ramble.app.builtin.osu-micro-benchmarks import OsuMicroBenchmarks as OsuMicroBenchmarksBase


class OsuMicroBenchmarks(OsuMicroBenchmarksBase):

    tags = ['synthetic',
            'large-scale','multi-node','single-node',
            'atomics','managed-memory',
            'mpi','openshmem','upc','upc++','nccl','rccl',
            'network-bandwidth-bound','network-bisection-bandwidth-bound',
            'network-collectives','network-latency-bound',
            'network-multi-threaded','network-nonblocking-collectives',
            'network-onesided','network-point-to-point',
            'c','java','python','cuda','rocm','openacc']
