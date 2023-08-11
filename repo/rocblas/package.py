from spack.package import *
from spack.pkg.builtin.rocblas import Rocblas as BuiltinRocblas

class Rocblas(BuiltinRocblas):

    provides("blas")

