from spack.package import *
from spack.pkg.builtin.cray_mpich import CrayMpich as BuiltinCM

class CrayMpich(BuiltinCM):

    variant("gpu-aware", default=False, description="enable GPU-aware mode")

    def setup_run_environment(self, env):

        super(CrayMpich, self).setup_run_environment(env)

        if self.spec.satisfies("+gpu-aware"):
            env.set("MPICH_GPU_SUPPORT_ENABLED", "1")
            env.prepend_path("LD_LIBRARY_PATH", self.spec.extra_attributes["gtl_lib_path"])
            env.set("GTL_HSA_VSMSG_CUTOFF_SIZE", str(self.spec.extra_attributes["gtl_cutoff_size"]))
            env.set("FI_CXI_ATS", str(self.spec.extra_attributes["fi_cxi_ats"]))
        else:
            env.unset("MPICH_GPU_SUPPORT_ENABLED")
            env.prepend_path("LD_LIBRARY_PATH", self.spec.extra_attributes["gtl_lib_path"])
