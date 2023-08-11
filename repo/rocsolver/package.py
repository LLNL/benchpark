from spack.package import *
from spack.pkg.builtin.rocsolver import Rocsolver as BuiltinRocsolver

class Rocsolver(BuiltinRocsolver):

    provides("lapack")
