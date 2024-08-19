
from spack.package import *

class Phloem(MakefilePackage):
    tags = []

    url = "https://github.com/LLNL/phloem/archive/refs/tags/v1.4.5.tar.gz"
    git = "https://github.com/LLNL/phloem"

    maintainers("knox10")

    version("master", branch="master")

    variant("mpi", default=False, description="Build with MPI support")
    
    depends_on("mpi", when="+mpi")

    #@property
    #def build_targets(self):
        #targets = ["all"]
      #  spec=self.spec
       # if "+mpi" in spec:
        #    targets.append("CC={0}".format(spec["mpi"].mpicxx))dd
        #return targets

    #def edit(self, spec, prefix):
     #   makefile = FileFilter("Makefile")
      #  makefile.filter('CC = cc', "CC = {0}".format(spec["mpi"].mpicc))


    def install(self, spec, prefix):
        mkdir(prefix.bin)
        mkdir(prefix.doc)
        install("mpigraph-1.6/mpiBench/mpiBench", prefix.bin)
        install("sqmr-1.1.0/sqmr", prefix.bin)
        install("README", prefix.doc)
