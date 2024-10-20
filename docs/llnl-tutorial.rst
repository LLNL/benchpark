.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

=====================
Tutorial: LLNL System
=====================

.. note::

    We might add console outputs for these, so users know what to expect

This tutorial will guide you through the process of using Benchpark on an LLNL
system (Tioga?). In this case, we assume the ``system``, and the ``benchmark``
and ``experiment`` are already configured.

First, we initialize the system for LLNL's tioga system using the existing
system specification in Benchpark::

    benchpark system init --dest=tioga-system tioga

We want to run the Saxpy benchmark, so we initialize it for experiments::

    benchpark experiment init --dest=saxpy-benchmark saxpy programming_model=openmp

Next, we need to setup our dependency software, Ramble and Spack::

    . workspace/setup.sh

We setup the Saxpy workspace::

    cd ./workspace/saxpy/openmp/$ARCHCONFIG/workspace/
    ramble --workspace-dir . --disable-progress-bar --disable-logger workspace setup

Next, we run the Saxpy experiments, which will launch jobs through the
scheduler on Tioga::

    ramble --workspace-dir . --disable-progress-bar --disable-logger on
