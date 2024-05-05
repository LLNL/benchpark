.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==============================
Running benchpark on Fugaku
==============================

Get in interactive shell

    pjsub --interact ...

Load newer python environment

    if [ -f ~/spack/share/spack/setup-env.sh ]; then
        source ~/spack/share/spack/setup-env.sh;
    else
        source /vol0004/apps/oss/spack/share/spack/setup-env.sh;
    fi
    spack load python@3.10.8 /mzi2ihx; spack load py-pip@23.1.2 /4hkqlma

Follow instructions in :doc:`1-getting-started`.

Set up the directory structure for your experiment

    export BM='saxpy/openmp'
    export SYS='RCCS-Fugaku-Fujitsu-A64FX-TofuD'
    ./bin/benchpark setup ${BM} ${SYS} workspace

Patch some files in various repos

    sed -i -e "s@1280000000@160000000@g" -e 's@cflags=".*"@@g' experiments/streamc/openmp/ramble.yaml
    wget https://raw.githubusercontent.com/GoogleCloudPlatform/ramble/22db33d5f3728e015fcca6d5618a67014ca132c8/lib/ramble/ramble/spack_runner.py -O workspace/ramble/lib/ramble/ramble/spack_runner.py
    wget https://raw.githubusercontent.com/jdomke/spack/RIKEN_CCS_fugaku5/lib/spack/spack/util/libc.py -O workspace/spack/lib/spack/spack/util/libc.py
    wget https://raw.githubusercontent.com/jdomke/spack/RIKEN_CCS_fugaku6/var/spack/repos/builtin/packages/hpcg/package.py -O workspace/spack/var/spack/repos/builtin/packages/hpcg/package.py
    wget https://raw.githubusercontent.com/jdomke/spack/RIKEN_CCS_fugaku8/var/spack/repos/builtin/packages/fujitsu-mpi/package.py -O workspace/spack/var/spack/repos/builtin/packages/fujitsu-mpi/package.py
    wget https://raw.githubusercontent.com/jdomke/spack/RIKEN_CCS_fugaku9/var/spack/repos/builtin/packages/fujitsu-ssl2/package.py -O workspace/spack/var/spack/repos/builtin/packages/fujitsu-ssl2/package.py

Build the benchmark

    source ./workspace/setup.sh
    export TMP=/local
    export TMPDIR=/local
    ramble -P -D $(readlink -f $(pwd)/workspace/${BM}/${SYS}/workspace) workspace setup

Submit benchmarks from login node (not interactive shell)

    if [ -f ~/spack/share/spack/setup-env.sh ]; then
        source ~/spack/share/spack/setup-env.sh;
    else
        source /vol0004/apps/oss/spack/share/spack/setup-env.sh;
    fi
    spack load python@3.11.6 /yjlixq5
    export BM='saxpy/openmp'
    export SYS='RCCS-Fugaku-Fujitsu-A64FX-TofuD'
    ramble -P -D $(readlink -f $(pwd)/workspace/${BM}/${SYS}/workspace) on

