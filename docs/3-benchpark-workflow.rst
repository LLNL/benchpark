.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

=================================
Benchpark Workflow
=================================

Follow the workflow diagram to determine how many new configurations are
required. If you are running on an existing ``system``, and the ``benchmark``
and ``experiment`` are already configured, you can proceed directly to
:doc:`4-benchpark-setup`.

.. image:: /_static/images/new-workflow.png

Otherwise, you will be editing one or more of the files below.

Benchpark configuration files are organized as follows::

  $benchpark
  ├── var
  |  ├── exp_repo
  |  |  └── experiments
  |  |     └── ${BENCHMARK1}
  |  |        └── experiment.py
  |  └── sys_repo
  |     └── systems
  |        └── ${SYSTEM1}
  |           ├── system.py
  |           ├── compilers
  |           └── externals
  └── repo
     ├── ${BENCHMARK1}
     │  ├── application.py
     │  └── package.py
     └── repo.yaml



System Specification
--------------------
Files under ``benchpark/var/sys_repo/systems/${SYSTEM}`` provide the specification
of the software stack on your system:

* Find a similar ``system``: :doc:`identifying-similar-system`

* Add or edit a ``system``: :doc:`add-a-system-config`


Benchmark Specification
-----------------------
If you would like to modify a specification of your benchmark,
you can do so by upstreaming changes to Spack and/or Ramble,
or working on your benchmark specification in ``benchpark/repo/${BENCHMARK}``:

* Add a ``benchmark``: :doc:`add-a-benchmark`


Experiment Specification
------------------------
Files under ``benchpark/var/exp_repo/experiments/${BENCHMARK}/${ProgrammingModel}``
provide the specifications for the experiments.
If you would like to make changes to your experiments,  such as enabling
specific tools to measure the performance of your experiments,
you can manually edit the specifications in ``ramble.yaml``:

* Add/edit an ``experiment``: :doc:`add-an-experiment`


