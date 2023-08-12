#!/bin/bash

TEST_NAME=raja-perf \
TEST_CONFIG_NAME=ats2 \
TEST_SOURCE_DIR=/g/g23/haque1/coral-2/benchpark/raja-perf \
TEST_WORKING_ROOT=/p/gpfs1/haque1 \
./rambler.sh
#TEST_SOURCE_DIR=/${HOME}/benchpark/${TEST_NAME} \
#TEST_WORKING_ROOT=/p/lustre/${USER} \
