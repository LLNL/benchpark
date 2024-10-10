# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

import benchpark.repo


sys_repo = benchpark.repo.paths[benchpark.repo.ObjectTypes.systems]
exp_repo = benchpark.repo.paths[benchpark.repo.ObjectTypes.experiments]


def setup_parser(subparser):
    pass


def audit_experiment(exp_cls):
    required_methods = ["compute_applications_section"]

    errors = list()

    for method in required_methods:
        if method  not in exp_cls.__dict__:
            errors.append(f"{exp_cls.__name__} does not implement {method}")

    return errors


def command(args):
    all_errors = list()

    for exp_name in exp_repo.all_object_names():
        exp_cls = exp_repo.get_obj_class(exp_name)
        all_errors.extend(audit_experiment(exp_cls))

    for error in all_errors:
        print(error)

    if all_errors:
        sys.exit(1)
