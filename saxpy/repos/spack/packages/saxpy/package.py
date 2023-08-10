from spack.package import *
import os

class Saxpy(CMakePackage, CudaPackage, ROCmPackage):
    """Test saxpy problem."""

    homepage = "https://example.com"
    url = "file://{0}/srcs/saxpy_src.tar.gz".format(os.getcwd())
    tags = ["benchmark"]

    test_requires_compiler = True

    version('1.0.0', '8f0f17e5c0af35627fc58075249357bfb59795f892239786ddab9cdd5ee414f1', extension="tar.gz")

    variant("openmp", default=True, description="Enable OpenMP support")

    conflicts("+cuda", when="+rocm+openmp")
    conflicts("+rocm", when="+cuda+openmp")
    conflicts("+openmp", when="+rocm+cuda")

    depends_on("cmake")
    depends_on("mpi")

    def setup_build_environment(self, env):
      if "+cuda" in self.spec:
        env.set("CUDAHOSTCXX", self.spec["mpi"].mpicxx)
      if self.spec["mpi"].extra_attributes and "gtl_lib_path" in self.spec["mpi"].extra_attributes:
        env.prepend_path("LD_LIBRARY_PATH", self.spec['mpi'].extra_attributes["gtl_lib_path"])

    def setup_run_environment(self, env):
      if self.spec["mpi"].extra_attributes and "gtl_lib_path" in self.spec["mpi"].extra_attributes:
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
