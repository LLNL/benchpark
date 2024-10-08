#!/bin/bash

../../bin/benchpark setup saxpy/openmp x86 ../../../llnl-weekly
../../bin/benchpark setup amg2023/openmp x86 ../../../llnl-weekly
../../bin/benchpark setup raja-perf/openmp x86 ../../../llnl-weekly


ramble workspace create -d merged_suite
ramble workspace activate merged_suite
cat >> merged_suite/configs/ramble.yaml << EOF
ramble:
  include:
  - saxpy/openmp/ramble.yaml
  - amg2023/openmp/ramble.yaml
  - raja-perf/openmp/ramble.yaml
EOF
