.. Copyright 2023 Lawrence Livermore National Security, LLC and other
   Benchpark Project Developers. See the top-level COPYRIGHT file for details.

   SPDX-License-Identifier: Apache-2.0

==============================
Dependency on Spack and Ramble
==============================

Benchpark depends on the build functionality provided in
`Spack <https://github.com/spack/spack>`_,
and run functionality provided in
`Ramble <https://github.com/GoogleCloudPlatform/ramble>`_.
To allow for testing before pulling in updates in Spack and Ramble,
Benchpark clones and uses the versions of Spack and Ramble
specified in ``checkout-versions.yaml``.

The user might notice this delay in Spack and Ramble versions
in two ways:
* The latest functionality of Spack and/or Ramble may not yet be
  available in Benchpark.
* The latest package.py specifications available in Spack
  and application.py specifications available in Ramble
  may not be available in Benchpark.

At your own risk, you may go into the cloned Spack and Ramble
directories and perform a git pull to grab those updates.
This may be useful for package updates, but perilous for
functionality updates.

Alternatively, the user may temporarily copy the needed packages
into ``benchpark/repo``, and remove them when Benchpark updates
to the next version of Spack/Ramble.
