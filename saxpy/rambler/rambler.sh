#!/bin/bash

if [ -z "${TEST_SOURCE_DIR}" ]; then
    echo "Missing benchpark source path. Set TEST_SOURCE_DIR in ${TEST_CONFIG_NAME}.sh"
    exit 1
else
    echo "Benchpark source directory: ${TEST_SOURCE_DIR}"
fi

if [ -z "${TEST_WORKING_ROOT}" ]; then
    echo "Missing working directory path. Set TEST_WORKING_ROOT in ${TEST_CONFIG_NAME}.sh"
    exit 1
else
    echo "Working directory: ${TEST_WORKING_ROOT}"
fi

rm -rf /tmp/${USER}/spack-stage/*
rm -rf ~/.spack/cache
rm -rf ~/.spack/bootstrap
rm -rf ~/.spack/linux/compiler.yaml
rm -rf ~/.spack/packages.yaml
rm -rf ~/.spack/repos.yaml
rm -rf ~/.ramble/repos.yaml

TEST_WORKING_DIR=${TEST_WORKING_ROOT}/${TEST_NAME}/${TEST_CONFIG_NAME}
TEST_SOURCE_CONFIG_DIR=${TEST_SOURCE_DIR}/${TEST_CONFIG_NAME}

mkdir -p ${TEST_SOURCE_DIR}
mkdir -p ${TEST_SOURCE_CONFIG_DIR}

rm -rf ${TEST_WORKING_DIR}
mkdir -p ${TEST_WORKING_DIR}
mkdir ${TEST_WORKING_DIR}/workspace
mkdir -p ${TEST_WORKING_DIR}/workspace/configs/auxiliary_software_files
mkdir ${TEST_WORKING_DIR}/repos
mkdir ${TEST_WORKING_DIR}/workspace/srcs

lndir -silent ${TEST_SOURCE_CONFIG_DIR}/configs ${TEST_WORKING_DIR}/workspace/configs
lndir -silent ${TEST_SOURCE_DIR}/repos ${TEST_WORKING_DIR}/repos
lndir -silent ${TEST_SOURCE_DIR}/srcs ${TEST_WORKING_DIR}/workspace/srcs
git clone -c feature.manyFiles=true https://github.com/spack/spack.git ${TEST_WORKING_DIR}/spack

TEST_REPO_NAMESPACE=${TEST_NAME}-repo
echo "repo:
  namespace: ${TEST_REPO_NAMESPACE}
" > ${TEST_WORKING_DIR}/repos/spack/repo.yaml

echo "repos:
- ${TEST_WORKING_DIR}/repos/spack
" > ${TEST_WORKING_DIR}/workspace/configs/auxiliary_software_files/repos.yaml

git clone -c feature.manyFiles=true https://github.com/GoogleCloudPlatform/ramble.git ${TEST_WORKING_DIR}/ramble
cd ${TEST_WORKING_DIR}/workspace

echo "repo:
  namespace: ${TEST_REPO_NAMESPACE}
" > ${TEST_WORKING_DIR}/repos/ramble/repo.yaml

echo "repos:
- ${TEST_WORKING_DIR}/repos/ramble
" > ${TEST_WORKING_DIR}/workspace/configs/repos.yaml

echo "
cd ${TEST_WORKING_DIR}/workspace

. ${TEST_WORKING_DIR}/spack/share/spack/setup-env.sh
. ${TEST_WORKING_DIR}/ramble/share/ramble/setup-env.sh

ramble -D . workspace setup
ramble -D . on
"
