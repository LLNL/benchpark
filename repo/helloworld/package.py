# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install helloworld
#
# You can edit this file again by typing:
#
#     spack edit helloworld
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Helloworld(MakefilePackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://www.example.com"
    url = "https://github.com/august-knox/helloWorld/archive/refs/tags/v1.5.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers("github_user1", "github_user2")

    # FIXME: Add the SPDX identifier of the project's license below.
    # See https://spdx.org/licenses/ for a list. Upon manually verifying
    # the license, set checked_by to your Github username.
    license("UNKNOWN", checked_by="github_user1")

    version("1.5", sha256="c0a3458fd151af7471cc31d250a79b1850567b9c901741e96ad8a5e1c6df2a68")
    version("1.4", sha256="7ef028b04ce70fbeb997cb3d5fc14d93d288d1964bb2e848f082debf93db6fef")
    version("1.3", sha256="7e9034d08a6132309e23085e4e14218e9e088594adb53cdf9a56b2bed8d365f6")
    version("1.2", sha256="18cfa58756cf99d4322147b708bef2ba80ae90b5356e0ffbe0e2438efbc113e8")
    version("1.1", sha256="56e2d4ff6b10f848da1307fdd8f219cae7db216be8703dc8a96248f840305237")

    # FIXME: Add dependencies if required.
    # depends_on("foo")

    def install(self, spec, prefix):
        mkdir(prefix.bin)
        install("helloworld", prefix.bin)
