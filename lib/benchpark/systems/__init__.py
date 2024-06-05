# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from .aws import Aws

sys_id_to_class = {
    "aws": Aws,
}


def system_from_type(type_id, **kwargs):
    cls = sys_id_to_class.get(type_id, None)
    if not cls:
        raise ValueError(f"No system type matching: {type_id}")
    return cls(**kwargs)
