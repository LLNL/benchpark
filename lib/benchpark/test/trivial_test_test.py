# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0
import pytest


def test_trivial_pass():
    assert True


@pytest.mark.xfail
def test_trivial_fail():
    assert False
