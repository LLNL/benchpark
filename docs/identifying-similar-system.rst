.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==============================
Identifying a Similar System
==============================

The easiest place to start when configuring a new system is to find the closest similar
one that has an existing configuration already. Existing system configurations are listed
in the table in :doc:`system-list`. 

If you are running on a system with an accelerator, find an existing system wih the same accelerator vendor,
and then secondarily, if you can, match the actual accererator. 

1. accelerator.vendor
2. accelerator.name

Once you have found an existing system with a similar accelerator or if you do not have an accelerator, 
match the following processor specs as closely as you can. 

1. processor.name
2. processor.ISA 
3. processor.uArch

If there is not an exact match that is okay, we provide steps for customizing the configuration to match your system in :doc:`add-a-system-config`.





