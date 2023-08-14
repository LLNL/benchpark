from spack.package import *
from spack.pkg.builtin.hypre import Hypre as BuiltinHypre

import os

class Hypre(BuiltinHypre):
    requires("+rocm", when="^rocblas")
    requires("+rocm", when="^rocsolver")

    def configure_args(self):
        spec = self.spec

        configure_args = [
            "--prefix=%s" % prefix,
        ]

        if "+mpi" in spec:
            configure_args.append("--with-MPI")
            configure_args.append("--with-MPI-lib-dirs={0}".format(spec["mpi"].prefix.lib))
            configure_args.append("--with-MPI-include={0}".format(spec["mpi"].prefix.include))
            if spec.satisfies("^cray-mpich+gtl"):
                configure_args.append("--enable-gpu-aware-mpi")
        else:
            configure_args.append("--without-MPI")

        if "+verbose" in spec:
            configure_args.append("--verbose")

        # Note: --with-(lapack|blas)_libs= needs space separated list of names
        lapack = spec["lapack"].libs
        blas = spec["blas"].libs
        configure_args.append("--with-lapack-libs=%s" % " ".join(lapack.names)),
        configure_args.append("--with-lapack-lib-dirs=%s" % " ".join(lapack.directories)),
        configure_args.append("--with-blas-libs=%s" % " ".join(blas.names)),
        configure_args.append("--with-blas-lib-dirs=%s" % " ".join(blas.directories)),

        if self.spec["blas"].satisfies("rocblas"):
            configure_args.append("--enable-rocblas")
        if self.spec["lapack"].satisfies("rocsolver"):
            rocm_rpath_flag = f"-Wl,-rpath,{os.path.dirname(spec['lapack'].prefix)}/lib"
            sep = " " if "LDFLAGS" in os.environ else ""
            os.environ["LDFLAGS"] = os.environ.get("LDFLAGS", "") + sep + rocm_rpath_flag

        if "+mpi" in spec and not spec.satisfies("^cray-mpich~wrappers"):
            os.environ["CC"] = spec["mpi"].mpicc
            os.environ["CXX"] = spec["mpi"].mpicxx
            if "+fortran" in spec:
                os.environ["F77"] = spec["mpi"].mpif77
                os.environ["FC"] = spec["mpi"].mpifc
        else:
            os.environ["CC"] = spack_cc
            os.environ["CXX"] = spack_cxx
            if "+fortran" in spec:
                os.environ["F77"] = spack_f77
                os.environ["FC"] = spack_fc

        if "+mpi" in spec:
            if spec["mpi"].extra_attributes and "ldflags" in spec["mpi"].extra_attributes:
                if "LDFLAGS" in os.environ:
                  os.environ["LDFLAGS"] += " " + spec["mpi"].extra_attributes["ldflags"]
                else:
                  os.environ["LDFLAGS"] = spec["mpi"].extra_attributes["ldflags"]

        configure_args.extend(self.with_or_without("openmp"))

        if "+int64" in spec:
            configure_args.append("--enable-bigint")
        else:
            configure_args.append("--disable-bigint")

        configure_args.extend(self.enable_or_disable("mixedint"))

        configure_args.extend(self.enable_or_disable("complex"))

        if "+shared" in spec:
            configure_args.append("--enable-shared")

        if "~internal-superlu" in spec:
            configure_args.append("--without-superlu")
            # MLI and FEI do not build without superlu on Linux
            configure_args.append("--without-mli")
            configure_args.append("--without-fei")

        if "+superlu-dist" in spec:
            configure_args.append(
                "--with-dsuperlu-include=%s" % spec["superlu-dist"].prefix.include
            )
            configure_args.append("--with-dsuperlu-lib=%s" % spec["superlu-dist"].libs)
            configure_args.append("--with-dsuperlu")

        if "+umpire" in spec:
            configure_args.append("--with-umpire-include=%s" % spec["umpire"].prefix.include)
            configure_args.append("--with-umpire-lib=%s" % spec["umpire"].libs)
            if "~cuda~rocm" in spec:
                configure_args.append("--with-umpire-host")
            else:
                configure_args.append("--with-umpire")

        configure_args.extend(self.enable_or_disable("debug"))

        if "+cuda" in spec:
            configure_args.extend(["--with-cuda", "--enable-curand", "--enable-cusparse"])
            cuda_arch_vals = spec.variants["cuda_arch"].value
            if cuda_arch_vals:
                cuda_arch_sorted = list(sorted(cuda_arch_vals, reverse=True))
                cuda_arch = cuda_arch_sorted[0]
                configure_args.append("--with-gpu-arch={0}".format(cuda_arch))
            # New in 2.21.0: replaces --enable-cub
            if "@2.21.0:" in spec:
                configure_args.append("--enable-device-memory-pool")
                configure_args.append("--with-cuda-home={0}".format(spec["cuda"].prefix))
            else:
                configure_args.append("--enable-cub")
        else:
            configure_args.extend(["--without-cuda", "--disable-curand", "--disable-cusparse"])
            if "@:2.20.99" in spec:
                configure_args.append("--disable-cub")

        if "+rocm" in spec:
            rocm_pkgs = ["rocsparse", "rocthrust", "rocprim", "rocrand"]
            rocm_inc = ""
            for pkg in rocm_pkgs:
                if "^" + pkg in spec:
                    rocm_inc += spec[pkg].headers.include_flags + " "
            configure_args.extend(
                [
                    "--with-hip",
                    "--enable-rocrand",
                    "--enable-rocsparse",
                    "--with-extra-CUFLAGS={0}".format(rocm_inc),
                ]
            )
            rocm_arch_vals = spec.variants["amdgpu_target"].value
            if rocm_arch_vals:
                rocm_arch_sorted = list(sorted(rocm_arch_vals, reverse=True))
                rocm_arch = rocm_arch_sorted[0]
                configure_args.append("--with-gpu-arch={0}".format(rocm_arch))
        else:
            configure_args.extend(["--without-hip", "--disable-rocrand", "--disable-rocsparse"])

        if "+sycl" in spec:
            configure_args.append("--with-scyl")
            sycl_compatible_compilers = ["dpcpp", "icpx"]
            if not (os.path.basename(self.compiler.cxx) in sycl_compatible_compilers):
                raise InstallError(
                    "Hypre's SYCL GPU Backend requires DPC++ (dpcpp)"
                    + " or the oneAPI CXX (icpx) compiler."
                )

        if "+unified-memory" in spec:
            configure_args.append("--enable-unified-memory")

        configure_args.extend(self.enable_or_disable("fortran"))

        return configure_args

    def setup_build_environment(self, env):
        spec = self.spec
        if "+mpi" in spec and not spec.satisfies("^cray-mpich~wrappers"):
            env.set("CC", spec["mpi"].mpicc)
            env.set("CXX", spec["mpi"].mpicxx)
            if "+fortran" in spec:
                env.set("F77", spec["mpi"].mpif77)
                env.set("FC", spec["mpi"].mpifc)
        else:
            env.set("CC", spack_cc)
            env.set("CXX", spack_cxx)
            if "+fortran" in spec:
                env.set("F77", spack_f77)
                env.set("FC", spack_fc)

        if "+cuda" in spec:
            env.set("CUDA_HOME", spec["cuda"].prefix)
            env.set("CUDA_PATH", spec["cuda"].prefix)
            # In CUDA builds hypre currently doesn't handle flags correctly
            env.append_flags("CXXFLAGS", "-O2" if "~debug" in spec else "-g")

        if "+rocm" in spec:
            # As of 2022/04/05, the following are set by 'llvm-amdgpu' and
            # override hypre's default flags, so we unset them.
            env.unset("CFLAGS")
            env.unset("CXXFLAGS")

        #TODO: Add -fopenmp in ramble.yaml::spack_spec instead
        if "+openmp" in spec:
            env.append_flags("CFLAGS", "-fopenmp")
            env.append_flags("CXXFLAGS", "-fopenmp")
            env.append_flags("LDFLAGS", "-fopenmp")
