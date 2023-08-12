from spack.package import *
from spack.pkg.builtin.cray_mpich import CrayMpich as BuiltinCM

class CrayMpich(BuiltinCM):

    variant("gpu-aware", default=False, description="enable GPU-aware mode")

    def setup_run_environment(self, env):

        super(CrayMpich, self).setup_run_environment(env)

        if self.spec.satisfies("+gpu-aware"):
            env.set("MPICH_GPU_SUPPORT_ENABLED", "1")
            env.prepend_path("LD_LIBRARY_PATH", self.spec.extra_attributes["gtl_lib_path"])
        else:
            env.unset("MPICH_GPU_SUPPORT_ENABLED")
            env.prepend_path("LD_LIBRARY_PATH", self.spec.extra_attributes["gtl_lib_path"])
