=========
Benchpark setup
=========

Python 3.6 and git are required to check out and install Benchpark::

  git clone git@github.com:LLNL/benchpark.git $benchpark  
  benchpark setup [--spack=spack_dir] [--ramble=ramble_dir]

Benchpark uses the following open source projects for specifying configurations:

* `Ramble <https://github.com/GoogleCloudPlatform/ramble>`_ to specify run configurations
* `Spack <https://github.com/spack/spack>`_ to specify build configurations

If you already have Spack and/or Ramble on your system and you want to use these
installs, simply point Benchpark at these installs by passing in their locations.


What the ``benchpark setup`` script does for you
-----------------------------------------

``benchpark setup`` installs Spack and Ramble. If you are running into any issues with either,
please see the detailed installation instructions in those projects' docs.

Spack: https://spack.readthedocs.io/en/latest/getting_started.html#installation 

Ramble: https://googlecloudplatform.github.io/ramble/getting_started.html#installation 
