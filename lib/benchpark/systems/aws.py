# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from .base import System

# Taken from https://aws.amazon.com/ec2/instance-types/
# With boto3, we could determine this dynamically vs. storing a static table
id_to_resources = {
    "c4.xlarge": {
        "sys_cores_per_node": 4,
        "sys_mem_per_node": 7.5,
    },
    "c6g.xlarge": {
        "sys_cores_per_node": 4,
        "sys_mem_per_node": 8,
    },
}


class Aws(System):
    def __init__(self, instance_type=None):
        super().__init__()
        self.scheduler = "mpi"
        attrs = id_to_resources.get(instance_type)
        for k, v in attrs.items():
            setattr(self, k, v)
