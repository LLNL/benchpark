from spack.package import *
import os
import shutil
import spack.repo

class Saxpy(CMakePackage, CudaPackage, ROCmPackage):
    """Test saxpy problem."""

    homepage = "https://example.com"
    tags = ["benchmark"]

    has_code = False
    test_requires_compiler = True

    version('1.0.0')

    variant("openmp", default=True, description="Enable OpenMP support")

    conflicts("+cuda", when="+rocm+openmp")
    conflicts("+rocm", when="+cuda+openmp")
    conflicts("+openmp", when="+rocm+cuda")

    depends_on("cmake")
    depends_on("mpi")

    @run_before("cmake")
    def stage_source(self):
        repo_path = os.path.dirname(spack.repo.PATH.package_path(self.name))
        for f in ["CMakeLists.txt", "saxpy.cc"]:
            shutil.copy2(os.path.join(repo_path, f), self.stage.source_path)

    def setup_build_environment(self, env):
        if "+cuda" in self.spec:
            env.set("CUDAHOSTCXX", self.spec["mpi"].mpicxx)
        if self.spec["mpi"].extra_attributes and "gtl_lib_path" in self.spec["mpi"].extra_attributes:
            if self.spec.satisfies("+rocm"):  # no gtl for cpu-only runs
                env.prepend_path("LD_LIBRARY_PATH", self.spec['mpi'].extra_attributes["gtl_lib_path"])

    def setup_run_environment(self, env):
        if self.spec["mpi"].extra_attributes and "gtl_lib_path" in self.spec["mpi"].extra_attributes:
            if self.spec.satisfies("+rocm"):  # no gtl for cpu-only runs
                env.prepend_path("LD_LIBRARY_PATH", self.spec['mpi'].extra_attributes["gtl_lib_path"])

    def cmake_args(self):
        spec = self.spec
        args = []

        args.append('-DCMAKE_CXX_COMPILER={0}'.format(spec["mpi"].mpicxx))

        if '+cuda' in spec:
            args.append('-DCMAKE_CUDA_HOST_COMPILER={0}'.format(spec["mpi"].mpicxx))
            args.append('-DCMAKE_CUDA_COMPILER={0}'.format(spec["cuda"].prefix + "/bin/nvcc"))
            args.append('-DUSE_CUDA=ON')
            cuda_arch_vals = spec.variants["cuda_arch"].value
            if cuda_arch_vals:
                cuda_arch_sorted = list(sorted(cuda_arch_vals, reverse=True))
                cuda_arch = cuda_arch_sorted[0]
                args.append('-DCMAKE_CUDA_ARCHITECTURES={0}'.format(cuda_arch))
            args.append('-DCMAKE_CXX_STANDARD=14')
            args.append('-DCMAKE_CUDA_STANDARD=14')

        if '+rocm' in spec:
            args.append('-DUSE_HIP=ON')
            rocm_arch_vals = spec.variants["amdgpu_target"].value
            args.append("-DROCM_PATH={0}".format(spec['hip'].prefix))
            if rocm_arch_vals:
                rocm_arch_sorted = list(sorted(rocm_arch_vals, reverse=True))
                rocm_arch = rocm_arch_sorted[0]
                args.append("-DROCM_ARCH={0}".format(rocm_arch))

        return args
