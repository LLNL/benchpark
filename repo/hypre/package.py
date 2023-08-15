from spack.package import *
from spack.pkg.builtin.hypre import Hypre as BuiltinHypre

import os

class Hypre(BuiltinHypre):
    requires("+rocm", when="^rocblas")
    requires("+rocm", when="^rocsolver")

    def configure_args(self):
        configure_args = super().configure_args()

        if self.spec["blas"].satisfies("rocblas"):
            configure_args.append("--enable-rocblas")
        if self.spec.satisfies("^cray-mpich+gtl"):
            configure_args.append("--enable-gpu-aware-mpi")

        return configure_args

    def setup_build_environment(self, env):
        super().setup_build_environment(env)

        spec = self.spec
        if "+mpi" in spec:
            if "+fortran" in spec:
                env.set("FC", spec["mpi"].mpifc)
            if spec["mpi"].extra_attributes and "ldflags" in spec["mpi"].extra_attributes:
                env.append_flags("LDFLAGS", spec["mpi"].extra_attributes["ldflags"])
        if spec["lapack"].satisfies("rocsolver"):
            rocm_rpath_flag = f"-Wl,-rpath,{os.path.dirname(spec['lapack'].prefix)}/lib"
            env.append_flags("LDFLAGS", rocm_rpath_flag)
