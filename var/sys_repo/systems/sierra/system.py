# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import tempfile

from benchpark.directives import variant
from benchpark.system import System


class Sierra(System):
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

    def system_specific_variables(self):
        return {"cuda_arch": "70"}

    def external_pkg_configs(self):
        externals = Sierra.resource_location / "externals"

        compiler = self.spec.variants["compiler"][0]
        cuda_ver = self.spec.variants["cuda"][0]

        selections = [externals / "base" / "00-packages.yaml"]
        # 00-version-10-1-243-packages.yaml  01-version-11-8-0-packages.yaml
        if cuda_ver == "10-1-243":
            selections.append(externals / "cuda" / "00-version-10-1-243-packages.yaml")
        elif cuda_ver == "11-8-0":
            selections.append(externals / "cuda" / "01-version-11-8-0-packages.yaml")

        mpi_cfgs = {
            (
                "clang-ibm",
                "11-8-0",
            ): """\
    - spec: spectrum-mpi@2023.06.28-clang-ibm-16.0.6-cuda-11.8.0-gcc-11.2.1
      prefix: /usr/tce/packages/spectrum-mpi/spectrum-mpi-rolling-release-clang-ibm-16.0.6-cuda-11.8.0-gcc-11.2.1
      extra_attributes:
        extra_link_flags: "-L/usr/tce/packages/spectrum-mpi/spectrum-mpi-rolling-release-clang-ibm-16.0.6-cuda-11.8.0-gcc-11.2.1 -lmpiprofilesupport -lmpi_ibm_usempi -lmpi_ibm_mpifh -lmpi_ibm"
        ldflags: "-lmpiprofilesupport -lmpi_ibm_usempi -lmpi_ibm_mpifh -lmpi_ibm"
""",
            (
                "xl-gcc",
                "11-8-0",
            ): """\
    - spec: spectrum-mpi@2023.06.28-cuda-11.8.0-gcc-11.2.1
      prefix: /usr/tce/packages/spectrum-mpi/spectrum-mpi-rolling-release-xl-2023.06.28-cuda-11.8.0-gcc-11.2.1
      extra_attributes:
        ldflags: "-lmpiprofilesupport -lmpi_ibm_usempi -lmpi_ibm_mpifh -lmpi_ibm"
""",
            (
                "xl",
                "10-1-243",
            ): """\
    - spec: spectrum-mpi@2022.08.19-cuda-10.1.243
      prefix: /usr/tce/packages/spectrum-mpi/spectrum-mpi-rolling-release-xl-2022.08.19-cuda-10.1.243
      extra_attributes:
        ldflags: "-lmpiprofilesupport -lmpi_ibm_usempi -lmpi_ibm_mpifh -lmpi_ibm"
""",
            (
                "clang",
                "11-8-0",
            ): """\
    - spec: spectrum-mpi@2022.08.19-clang16.0.6-cuda-11.8.0
      prefix: /usr/tce/packages/spectrum-mpi/spectrum-mpi-rolling-release-clang-16.0.6-cuda-11.8.0-gcc-11.2.1
      extra_attributes:
        ldflags: "-lmpiprofilesupport -lmpi_ibm_usempi -lmpi_ibm_mpifh -lmpi_ibm"
""",
            (
                "xl",
                "11-8-0",
            ): """\
    - spec: spectrum-mpi@2022.08.19-cuda-11.8.0
      prefix: /usr/tce/packages/spectrum-mpi/spectrum-mpi-rolling-release-xl-2022.08.19-cuda-11.8.0
      extra_attributes:
        ldflags: "-lmpiprofilesupport -lmpi_ibm_usempi -lmpi_ibm_mpifh -lmpi_ibm"
""",
        }

        cfg = mpi_cfgs[(compiler, cuda_ver)]
        full_cfg = f"""\
packages:
  mpi:
    externals:
{cfg}
"""
        gen_file = self.next_adhoc_cfg()
        with open(gen_file, "w") as f:
            f.write(full_cfg)
        selections.append(gen_file)

        return selections

    def _adhoc_cfgs(self):
        if not getattr(self, "_tmp_cfgs", None):
            self._tmp_cfgs = tempfile.mkdtemp()
            self._adhoc_cfg_idx = 0
        return self._tmp_cfgs

    def next_adhoc_cfg(self):
        basedir = self._adhoc_cfgs()
        self._adhoc_cfg_idx += 1
        return os.path.join(basedir, str(self._adhoc_cfg_idx))

    def compiler_configs(self):
        # values=("clang-ibm", "xl", "xl-gcc", "clang"),
        # values=("11-8-0", "10-1-243"),
        compiler_cfgs = {
            (
                "clang-ibm",
                "11-8-0",
            ): """\
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
            (
                "xl-gcc",
                "11-8-0",
            ): """\
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
            (
                "xl",
                "10-1-243",
            ): """\
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
            (
                "xl",
                "11-8-0",
            ): """\
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
            (
                "clang",
                "11-8-0",
            ): """\
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
""",
        }

        compiler = self.spec.variants["compiler"][0]
        cuda_ver = self.spec.variants["cuda"][0]
        cfg = compiler_cfgs[(compiler, cuda_ver)]
        full_cfg = f"""\
compilers:
{cfg}
"""
        gen_file = self.next_adhoc_cfg()
        with open(gen_file, "w") as f:
            f.write(full_cfg)

        selections = [gen_file]
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
