.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

=========================
What to rerun after edits
=========================

.. list-table:: I made changes.  What should I rerun?
   :widths: 35 65
   :header-rows: 1

   * - What I changed
     - Commands to rerun
   * - configs
     - ``ramble --disable-progress-bar --workspace-dir . workspace setup``
   * - benchmark's package.py
     - ``ramble --disable-progress-bar --workspace-dir . workspace setup``
   * - dependency of package.py
     - ``ramble --disable-progress-bar --workspace-dir . workspace setup``
   * - experiment parameters
     - delete ``workspace/experiments``
   * - wish to rerun experiments
     - delete ``workspace/experiments``
