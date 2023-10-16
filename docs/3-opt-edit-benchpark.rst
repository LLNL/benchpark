==============
Step-by-step Installation
==============

If the provided ``$benchpark`` script in `Getting Started <docs/getting-started.rst>`_
does not expose options you need, or fails on your system in one of the steps,
here is the list of steps ``$benchpark`` performs that you can follow step by step,
amending and restarting the process as necessary.

**Spack:** 
Benchpark requires Spack to build its experiment(s). 
If a default Spack installation is not available on the test system, 
it can be cloned from the github repository as follows:: 

  git clone --depth=1 -c feature.manyFiles=true https://github.com/spack/spack.git ${APP_WORKING_DIR}/spack 

Once a Spack installation is available, source the appropriate script for your shell::

  . ${APP_WORKING_DIR}/spack/share/spack/setup-env.sh  


Detailed Spack installation instructions are available at https://spack.readthedocs.io/en/latest/getting_started.html#installation 
 
**Ramble:**
Benchpark requires the Ramble framework to run and analyze its experiments. 
 
If a default Ramble installation is not available on the test system, 
it can be cloned from its github repository as follows:: 

  git clone --depth=1 -c feature.manyFiles=true https://github.com/GoogleCloudPlatform/ramble.git ${APP_WORKING_DIR}/ramble 


Once a Ramble installation is available, source the appropriate Ramble script for your shell::

  . ${APP_WORKING_DIR}/ramble /share/ramble/setup-env.sh 
 
Detailed Ramble installation instructions are available at: https://googlecloudplatform.github.io/ramble/getting_started.html#installation 
 
**Clean Environment:** 
Spack and Ramble files in default locations may interfere with the correct execution of experiments. 
It is therefore recommended to run with a clean environment::

  export SPACK_DISABLE_LOCAL_CONFIG=1 
  rm -rf ~/.ramble/repos.yaml 

