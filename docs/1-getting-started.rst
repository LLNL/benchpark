=========
Getting started with Benchpark
=========

Git is needed to clone Benchpark, and Python 3.6 is needed to run Benchpark::

  git clone git@github.com:LLNL/benchpark.git   
  cd benchpark

Clone Spack::

  git clone -c feature.manyFiles=true https://github.com/spack/spack.git

Once you have cloned Spack, we recommend sourcing the appropriate script for your shell::

  # For bash/zsh/sh
  $ . spack/share/spack/setup-env.sh
  
  # For tcsh/csh
  $ source spack/share/spack/setup-env.csh
  
  # For fish
  $ . spack/share/spack/setup-env.fish

Clone Ramble::

  git clone -c feature.manyFiles=true https://github.com/GoogleCloudPlatform/ramble.git

Once you have cloned Ramble, we recommend sourcing the appropriate script for your shell::

  # For bash/zsh/sh
  $ . ramble/share/ramble/setup-env.sh
  
  # For tcsh/csh
  $ source ramble/share/ramble/setup-env.csh
  
  # For fish
  $ . ramble/share/ramble/setup-env.fish
