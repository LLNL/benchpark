==========================================
FAQ: I made changes.  What should I rerun?
==========================================

.. list-table:: I made changes.  What should I rerun?
   :widths: 35 65
   :header-rows: 1

   * - What I changed
     - Commands to rerun
   * - configs
     - ``ramble -P -D . workspace setup``
   * - benchmark's package.py 
     - ``ramble -P -D . workspace setup``
   * - dependency of package.py
     - ``ramble -P -D . workspace setup``
   * - experiment parameters
     - delete ``workspace/experiments``
   * - wish to rerun experiments
     - delete ``workspace/experiments``
