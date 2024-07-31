# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib

from benchpark.system import System


class Tioga(System):
    def __init__(self):
        super().__init__()

        self.scheduler = "flux"
        self.sys_cores_per_node = "64"
        self.sys_gpus_per_node = "4"

    def generate_description(self, output_dir):
        super().generate_description(output_dir)

        sw_description = pathlib.Path(output_dir) / "software.yaml"

        with open(sw_description, "w") as f:
            f.write(self.sw_description())

    def sw_description(self):
        """This is somewhat vestigial: for the Tioga config that is committed
           to the repo, multiple instances of mpi/compilers are stored and
           and these variables were used to choose consistent dependencies.
           The configs generated by this class should only ever have one
           instance of MPI etc., so there is no need for that. The experiments
           will fail if these variables are not defined though, so for now
           they are still generated (but with more-generic values).
        """
        return """\
software:
  packages:
    default-compiler:
      pkg_spec: cce
    default-mpi:
      pkg_spec: cray-mpich
    compiler-rocm:
      pkg_spec: cce
    compiler-amdclang:
      pkg_spec: clang
    compiler-gcc:
      pkg_spec: gcc
    blas-rocm:
      pkg_spec: rocblas
    blas:
      pkg_spec: rocblas
    lapack-rocm:
      pkg_spec: rocsolver
    lapack:
      pkg_spec: cray-libsci
    mpi-rocm-gtl:
      pkg_spec: cray-mpich+gtl
    mpi-rocm-no-gtl:
      pkg_spec: cray-mpich~gtl
    mpi-gcc:
      pkg_spec: cray-mpich~gtl
    fftw:
      pkg_spec: intel-oneapi-mkl
"""
