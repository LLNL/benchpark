=========
Checkout benchpark
=========

Python 3.6 and git are required to check out and install Benchpark::

  git clone git@github.com:LLNL/benchpark.git $benchpark  
  benchpark setup [--spack=spack_dir] [--ramble=ramble_dir]

Benchpark uses the following open source projects for specifying configurations:

* `Ramble <https://github.com/GoogleCloudPlatform/ramble>`_ ro specify run configurations
* `Spack <https://github.com/spack/spack>`_ to specify build configurations

If you already have Spack and/or Ramble on your system and you want to use these
installs, simply point Benchpark at these installs by passing in their locations.


What the ``benchpark setup`` script does
-----------------------------------------

1 Clone the Spack and Ramble repositories. Skip this step if Spack/Ramble installation is already available::

  git clone --depth=1 -c feature.manyFiles=true https://github.com/spack/spack.git $workspace/spack
  git clone --depth=1 -c feature.manyFiles=true https://github.com/GoogleCloudPlatform/ramble.git $workspace/ramble

2 Source the Spack/Ramble shell scripts for your environment::

  . $workspace/spack/share/spack/setup-env.sh
  . $workspace/ramble/share/ramble/setup-env.sh

Detailed Spack installation instructions are available at 
https://spack.readthedocs.io/en/latest/getting_started.html#installation 

Detailed Ramble installation instructions are available at 
https://googlecloudplatform.github.io/ramble/getting_started.html#installation 

3 Clean the Spack and Ramble environment::

export SPACK_DISABLE_LOCAL_CONFIG=1
rm -rf ~/.ramble/repos.yaml
