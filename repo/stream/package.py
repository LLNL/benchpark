# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *


class Stream(MakefilePackage):
    """The STREAM benchmark is a simple synthetic benchmark program that
    measures sustainable memory bandwidth (in MB/s) and the corresponding
    computation rate for simple vector kernels."""

    homepage = "https://www.cs.virginia.edu/stream/ref.html"
    git = "https://github.com/jeffhammond/STREAM.git"

    version("5.10-caliper", git="https://github.com/daboehme/STREAM.git",
            branch="caliper-support")
    version("5.10", preferred=True)

    variant("openmp", default=False, description="Build with OpenMP support")

    variant("stream_array_size", default="none", description="Size of work arrays in elements")
    variant(
        "ntimes",
        default="none",
        description='STREAM runs each kernel "NTIMES" times and reports the *best* result',
    )
    variant("offset", default="none", description="Relative alignment between arrays")
    variant(
        "stream_type",
        default="none",
        values=("none", "float", "double", "int", "long"),
        description="Datatype of arrays elements",
    )
    variant("caliper", default=False, description="Enable Caliper/Adiak support")

    requires("@5.10-caliper", when="+caliper")

    depends_on("caliper", when="+caliper")
    depends_on("adiak@0.4:", when="+caliper")

    def edit(self, spec, prefix):
        makefile = FileFilter("Makefile")

        # Use the Spack compiler wrappers
        makefile.filter("CC = .*", "CC = {0}".format(spack_cc))
        makefile.filter("FC = .*", "FC = {0}".format(spack_f77))

        cflags = "-O2"
        fflags = "-O2"
        if "+openmp" in self.spec:
            cflags += " " + self.compiler.openmp_flag
            fflags += " " + self.compiler.openmp_flag
        if "%aocc" in self.spec:
            cflags += " -mcmodel=large -ffp-contract=fast -fnt-store"
        if "+caliper" in self.spec:
            cflags += " -DSTREAM_ENABLE_CALIPER"
            cflags += " -I{0}".format(self.spec["adiak"].prefix.include)
            cflags += " -I{0}".format(self.spec["caliper"].prefix.include)
            cflags += " -L{0} -ladiak".format(self.spec["adiak"].prefix.lib)
            cflags += " -L{0} -lcaliper".format(self.spec["caliper"].prefix.lib64)

        if self.spec.variants["stream_array_size"].value != "none":
            cflags += " -DSTREAM_ARRAY_SIZE={0}".format(
                self.spec.variants["stream_array_size"].value
            )
        if self.spec.variants["ntimes"].value != "none":
            cflags += " -DNTIMES={0}".format(self.spec.variants["ntimes"].value)
        if self.spec.variants["offset"].value != "none":
            cflags += " -DOFFSET={0}".format(self.spec.variants["offset"].value)
        if self.spec.variants["stream_type"].value != "none":
            cflags += " -DSTREAM_TYPE={0}".format(self.spec.variants["stream_type"].value)

        # Set the appropriate flags for this compiler
        makefile.filter("CFLAGS = .*", "CFLAGS = {0}".format(cflags))
        makefile.filter("FFLAGS = .*", "FFLAGS = {0}".format(fflags))

    def install(self, spec, prefix):
        # Manual installation
        mkdir(prefix.bin)
        install("stream_c.exe", prefix.bin)
        install("stream_f.exe", prefix.bin)
