.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==============================
Identifying a System with Similar Hardware
==============================

The easiest place to start when configuring a new system is to find the closest similar
one that has an existing configuration already. Existing system configurations are listed
in the table in :doc:`system-list`. 

From the perspective of setting up a benchpark system configuration, if the following 
specs match the system would be considered similar:

1. processor.name
2. processor.ISA 
3. processor.uArch

Optional additional matching can be determined by looking at:

1. accelerator.name
2. interconnect.name

If there is more than one that is similar from a hardware perspective, it can be further 
narrowed down in the next step when looking at software similarities (:doc:`identifying-system-software`).




