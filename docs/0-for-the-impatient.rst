.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==============================
Prerequisites
==============================

Python 3.9.12 or greater

The pip install command will give a warning to include your
``${HOME}/.local/bin directory`` in your ``PATH`` (if you needed
to install additional packages, and if that's where you put them).


==============================
Environment
==============================


::

    export PATH=${HOME}/.local/bin:${PATH}
    export BPROOT=${PWD}/benchpark
    export PATH=${BPROOT}/bin:${PATH}
    export WORKSPACE_DIR=${PWD}/workspace
    export SPACK_DISABLE_LOCAL_CONFIG=1
    export BPSITE=nosite-x86_64
    export BPEXPR=saxpy/openmp
    alias bp="benchpark"


==============================
One-time Setup
==============================

::

    mkdir ${WORKSPACE_DIR}
    cd ${BPROOT}/..
    git clone git@github.com:LLNL/benchpark.git
    cd benchpark
    pip install -r requirements.txt

==============================
Smoke test
==============================

::

    bp setup ${BPEXPR} ${BPSITE} ${WORKSPACE_DIR}
    . ${WORKSPACE_DIR}/setup.sh
    ramble -P -D ${WORKSPACE_DIR}/${BPEXPR}/${BPSITE}/workspace workspace setup
    ramble -P -D ${WORKSPACE_DIR}/${BPEXPR}/${BPSITE}/workspace on

==============================
Script
==============================

::

    #!/bin/bash
    export TAG=`date +"%F_%T"`

    # Where are we?
    export MACHINE=poodle

    # Set up directory structure
    export TOPDIR=/dev/shm/bp
    export TMPDIR=/dev/shm/bp/tmp
    export RESULTS_DIR=${HOME}/w/${MACHINE}/bp/results

    echo "Starting..." `date`                                                       2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    echo "[bp_test.sh] MACHINE="${MACHINE}                                          2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    echo "[bp_test.sh] TOPDIR="${TOPDIR}                                            2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    echo "[bp_test.sh] RESULTS_DIR="${RESULTS_DIR}                                  2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}

    mkdir -p ${TOPDIR}
    mkdir -p ${TMPDIR}
    mkdir -p ${RESULTS_DIR}

    # Modify path
    export PATH=${HOME}/.local/bin:${PATH}
    export PATH=${TOPDIR}/benchpark/bin:${PATH}
    echo "[bp_test.sh] PATH="${PATH}                                                2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}

    # Set up software environment
    echo "[bp_test.sh] module load python/3.11.5"                                   2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    #module load python/3.11.5                                                       2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    module load python/3.10.8

    # Set up benchpark parameters
    export BPSITE=nosite-x86_64
    export BPEXPR=saxpy/openmp
    export WORKSPACE_DIR=${TOPDIR}/workspace
    echo "[bp_test.sh] BPSITE="${BPEXPR}                                            2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    echo "[bp_test.sh] BPEXPR="${BPEXPR}                                            2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    echo "[bp_test.sh] WORKSPACE_DIR="${WORKSPACE_DIR}                              2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    mkdir -p ${WORKSPACE_DIR}

    # spack rituals
    export SPACK_DISABLE_LOCAL_CONFIG=1
    echo "[bp_test.sh] SPACK_DISABLE_LOCAL_CONFIG="${SPACK_DISABLE_LOCAL_CONFIG}    2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}

    # and we're off....
    cd ${TOPDIR}
    git clone git@github.com:LLNL/benchpark.git                                     2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    cd ./benchpark
    pip install -r requirements.txt                                                 2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}

    benchpark setup ${BPEXPR} ${BPSITE} ${WORKSPACE_DIR}                            2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    . ${WORKSPACE_DIR}/setup.sh                                                     2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    ramble -P -D ${WORKSPACE_DIR}/${BPEXPR}/${BPSITE}/workspace workspace setup     2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    #ramble -P -D ${WORKSPACE_DIR}/${BPEXPR}/${BPSITE}/workspace on
    echo "Completed" `date`                                                         2>>${RESULTS_DIR}/bp_stderr_${TAG} 1>>${RESULTS_DIR}/bp_stdout_${TAG}
    cd ${RESULTS_DIR}

