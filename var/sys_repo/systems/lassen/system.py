# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import pathlib

from benchpark.directives import variant
from benchpark.system import System


class Lassen(System):
    variant(
        "cuda",
        default="11-8-0",
        values=("11-8-0", "10-1-243"),
        description="CUDA version",
    )

    variant(
        "compiler",
        default="cce",
        values=("clang-ibm", "xl", "xl-gcc", "clang"),
        description="Which compiler to use",
    )

    def initialize(self):
        super().initialize()

        self.scheduler = "lsf"
        self.sys_cores_per_node = "44"
        self.sys_gpus_per_node = "4"

    def generate_description(self, output_dir):
        super().generate_description(output_dir)

        sw_description = pathlib.Path(output_dir) / "software.yaml"

        with open(sw_description, "w") as f:
            f.write(self.sw_description())

    def external_pkg_configs(self):
        externals = Tioga.resource_location / "externals"

        rocm = self.spec.variants["rocm"][0]
        gtl = self.spec.variants["gtl"][0]
        compiler = self.spec.variants["compiler"][0]

        selections = [externals / "base" / "00-packages.yaml"]
        if rocm == "543":
            selections.append(externals / "rocm" / "00-version-543-packages.yaml")
        elif rocm == "551":
            selections.append(externals / "rocm" / "01-version-551-packages.yaml")

        if compiler == "cce":
            if gtl == "true":
                selections.append(externals / "mpi" / "02-cce-ygtl-packages.yaml")
            else:
                selections.append(externals / "mpi" / "01-cce-ngtl-packages.yaml")
            selections.append(externals / "libsci" / "01-cce-packages.yaml")
        elif compiler == "gcc":
            selections.append(externals / "mpi" / "00-gcc-ngtl-packages.yaml")
            selections.append(externals / "libsci" / "00-gcc-packages.yaml")

        return selections

    def compiler_configs(self):
        #values=("clang-ibm", "xl", "xl-gcc", "clang"),
        #values=("11-8-0", "10-1-243"),
        compiler_cfgs = {
            ("clang-ibm", "11-8-0"): """\
- compiler:
    spec: clang@16.0.6-ibm-cuda-11.8.0-gcc-11.2.1
    paths:
      cc: /usr/tce/packages/clang/clang-ibm-16.0.6-cuda-11.8.0-gcc-11.2.1/bin/clang
      cxx: /usr/tce/packages/clang/clang-ibm-16.0.6-cuda-11.8.0-gcc-11.2.1/bin/clang++
      f77: /usr/tce/packages/xl/xl-2023.06.28-cuda-11.8.0-gcc-11.2.1/bin/xlf_r
      fc: /usr/tce/packages/xl/xl-2023.06.28-cuda-11.8.0-gcc-11.2.1/bin/xlf_r
    flags:
      cflags: -g -O2
      cxxflags: -g -O2 -std=c++17
      fflags: -g -O2
    operating_system: rhel7
    target: ppc64le
    modules: [cuda/11.8.0, clang/ibm-16.0.6-cuda-11.8.0-gcc-11.2.1]
    environment: {}
    extra_rpaths: []
""",
            ("xl-gcc", "11-8-0"): """\
- compiler:
    spec: xl@16.1.1-2023.06.28-cuda-11.8.0-gcc-11.2.1
    paths:
      cc: /usr/tce/packages/xl/xl-2023.06.28-cuda-11.8.0-gcc-11.2.1/bin/xlc
      cxx: /usr/tce/packages/xl/xl-2023.06.28-cuda-11.8.0-gcc-11.2.1/bin/xlC
      f77: /usr/tce/packages/xl/xl-2023.06.28-cuda-11.8.0-gcc-11.2.1/bin/xlf
      fc: /usr/tce/packages/xl/xl-2023.06.28-cuda-11.8.0-gcc-11.2.1/bin/xlf
    flags:
      cflags: -g -O2
      cxxflags: -g -O2 -std=c++14
      fflags: -g -O2
    operating_system: rhel7
    target: ppc64le
    modules: [cuda/11.8.0, xl/2023.06.28-cuda-11.8.0-gcc-11.2.1]
    environment: {}
    extra_rpaths: []
""",
            ("xl", "10-1-243"): """\
- compiler:
    spec: xl@16.1.1-2022.08.19-cuda10.1.243
    paths:
      cc: /usr/tce/packages/xl/xl-2022.08.19/bin/xlc
      cxx: /usr/tce/packages/xl/xl-2022.08.19/bin/xlC
      f77: /usr/tce/packages/xl/xl-2022.08.19/bin/xlf
      fc: /usr/tce/packages/xl/xl-2022.08.19/bin/xlf
    flags:
      cflags: -g -O2
      cxxflags: -g -O2 -std=c++14
      fflags: -g -O2
    operating_system: rhel7
    target: ppc64le
    modules: [cuda/10.1.243, xl/2022.08.19] # TODO: Make these available to ramble or remove them entirely
    environment: {}
    extra_rpaths: []
""",
            ("xl", "11-8-0"): """\
- compiler:
    spec: xl@16.1.1-2022.08.19-cuda11.8.0
    paths:
      cc: /usr/tce/packages/xl/xl-2022.08.19-cuda-11.8.0/bin/xlc
      cxx: /usr/tce/packages/xl/xl-2022.08.19-cuda-11.8.0/bin/xlC
      f77: /usr/tce/packages/xl/xl-2022.08.19-cuda-11.8.0/bin/xlf
      fc: /usr/tce/packages/xl/xl-2022.08.19-cuda-11.8.0/bin/xlf
    flags: # TODO: Fix spack concretization bug
      cflags: -g -O2
      cxxflags: -g -O2 -std=c++14
      fflags: -g -O2
    operating_system: rhel7
    target: ppc64le
    modules: [cuda/11.8.0, xl/2022.08.19-cuda-11.8.0] # TODO: Make these available to ramble or remove them entirely
    environment: {}
    extra_rpaths: []
""",
            ("clang", "11-8-0"): """\
- compiler:
    spec: clang@16.0.6-cuda11.8.0
    paths:
      cc: /usr/tce/packages/clang/clang-16.0.6-cuda-11.8.0-gcc-11.2.1/bin/clang
      cxx: /usr/tce/packages/clang/clang-16.0.6-cuda-11.8.0-gcc-11.2.1/bin/clang++
      f77: /usr/tce/packages/gcc/gcc-11.2.1/bin/gfortran
      fc: /usr/tce/packages/gcc/gcc-11.2.1/bin/gfortran
    flags:
      cflags: -g -O2
      cxxflags: -g -O2 -std=c++17
      fflags: ''
    operating_system: rhel7
    target: ppc64le
    modules: []
    environment: {}
    extra_rpaths: []
"""
        }

        compiler = self.spec.variants["compiler"][0]
        cuda_ver = self.spec.variants["cuda"][0]
        cfg = compiler_cfgs[(compiler, cuda_ver)]]
        full_cfg = f"""\
compilers:
{cfg}
"""

        return selections

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
      pkg_spec: clang
    default-mpi:
      pkg_spec: spectrum-mpi
    compiler-xl:
      pkg_spec: xl
    mpi-xl:
      pkg_spec: spectrum-mpi
    compiler-clang:
      pkg_spec: clang
    mpi-clang:
      pkg_spec: spectrum-mpi
    mpi-gcc:
      pkg_spec: spectrum-mpi
    compiler-clang-ibm:
      pkg_spec: clang
    mpi-clang-ibm:
      pkg_spec: spectrum-mpi
    blas:
      pkg_spec: cublas
    cublas-cuda:
      pkg_spec: cublas
    lapack:
      pkg_spec: lapack@3.9.0
    fftw:
      pkg_spec: fftw@3.3.10
"""
