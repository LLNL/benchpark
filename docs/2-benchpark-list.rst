.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

================
Search Benchpark
================

The user can search for available system and experiment specifications in Benchpark.

.. list-table:: Searching for specifications in Benchpark
   :widths: 25 25 50
   :header-rows: 1

   * - Command
     - Description
     - Listing in the docs
   * - benchpark list
     - Lists all benchmarks and systems specified in Benchpark
     - 
   * - benchpark list systems
     - Lists all system specified in Benchpark
     - :doc:`available-system-specs`
   * - benchmark list benchmarks
     - Lists all benchmarks specified in Benchpark
     - 
   * - benchpark list systems
     - Lists all system specified in Benchpark
     - :doc:`available-system-specs`
   * - benchpark tags workspace
     - Lists all tags specified in Benchpark
     - 
   * - benchpark tags -a application workspace
     - Lists all tags specified for a given application in Benchpark
     - 
   * - benchpark tags -t tag workspace
     - Lists all experiments in Benchpark with a given tag
     - 


Once you have decided on a ``system`` you will use, and the ``benchmark/ProgrammingModel``
to run, you can proceed to :doc:`4-benchpark-setup`.

For a complete list of options, see the help menu in :doc:`benchpark-help`.
