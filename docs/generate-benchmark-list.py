#!/usr/bin/env python3

import pandas as pd
import yaml
import os
import re
import sys
import subprocess


def construct_tag_groups(tag_groups, tag_dicts, dictionary):
    # everything is a dict
    for k, v in dictionary.items():
        if isinstance(v, list):
            tag_groups.append(k)
            tag_dicts[k] = v
        else:
            print("ERROR in construct_tag_groups")


def benchpark_benchmarks(benchmarks):
    experiments_dir = "../experiments"
    for x in os.listdir(experiments_dir):
        benchmarks.append(f"{x}")
    return benchmarks


def main(workspace):
    benchmarks = list()
    benchpark_benchmarks(benchmarks)

    f = "../tags.yaml"
    with open(f, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    tag_groups = []
    tag_dicts = {}
    for k, v in data.items():
        if k == "benchpark-tags":
            construct_tag_groups(tag_groups, tag_dicts, v)
        else:
            print("ERROR in top level construct_tag_groups")

    print("Tags in benchpark_tags:")
    for k, v in tag_dicts.items():
        print(k + ": " + str(v))
    print("\n")

    tags_benchmark_map = {}
    tags_benchmark_map["hpcc"] = ['DGEMM', 'benchmark', 'benchmark-app', 'mini-app']
    tags_benchmark_map["md-test"] = ['IO', 'synthetic-benchmarks']
    tags_benchmark_map["saxpy"] = ['c++', 'cuda', 'high-memory-bandwidth', 'hip', 'openmp', 'regular-memory-access', 'single-node']
    tags_benchmark_map["hpl"] = ['benchmark', 'benchmark-app', 'linpack']
    tags_benchmark_map["hpcg"] = ['benchmark', 'benchmark-app', 'mini-app']
    tags_benchmark_map["lammps"] = ['molecular-dynamics']
    tags_benchmark_map["osu-micro-benchmarks"] = ['synthetic-benchmarks']
    tags_benchmark_map["streamc"] = ['memory-benchmark', 'memorybenchmark', 'micro-benchmark', 'microbenchmark']
    tags_benchmark_map["amg2023"] = ['asc', 'block-structured-grid', 'c', 'cuda', 'engineering', 'high-branching', 'high-memory-bandwidth', 'hip', 'hypre', 'irregular-memory-access', 'large-memory-footprint', 'large-scale', 'mixed-precision', 'mpi', 'multi-node', 'network-collectives', 'network-latency-bound', 'openmp', 'regular-memory-access', 'single-node', 'solver', 'sparse-linear-algebra', 'sub-node']
    tags_benchmark_map["raja-perf"] = ['asc', 'atomics', 'c++', 'cuda', 'high-memory-bandwidth', 'hip', 'mpi', 'network-latency-bound', 'network-point-to-point', 'openmp', 'raja', 'register-pressure', 'regular-memory-access', 'simd', 'single-node', 'structured-grid', 'sub-node', 'sycl', 'vectorization']

    main = dict()

#d["amg"] = {
#    "appliation-domain": [asc, engineering],
#    "benchmark-scale": []
#}

    tags_taggroups = {}
    for bmark in benchmarks:
        tags_taggroups[bmark] = {}
        for k, v in tag_dicts.items():
            tags_taggroups[bmark][k] = []

#    for bmark, tags in tags_benchmark_map.items():
#        for t in tags:
#            for k, v in tag_dicts.items():
#                print(bmark, t, k, "filling tags_taggroups dict")
#        print("zero out tags_taggroups dict")
#        print("save to benchmark dict")

    for bmark in benchmarks:
        # call benchpark tags -a bmark workspace
        cmd = ["benchpark", "tags", "-a", bmark, workspace]
        print("RRR", cmd)
        tags = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    #for bmark, tags in tags_benchmark_map.items():
        for t in tags:
            for k, v in tag_dicts.items():
                if t in v:
                    print("appending", t, "at key", k)
                    tags_taggroups[bmark][k].append(t)
        main[bmark] = tags_taggroups[bmark]
        #tags_taggroups = tags_taggroups.fromkeys(tags_taggroups, [])

#    for bmark, v in main.items():
#        print(bmark)
#        print(v)
#        print("\n")

    df = pd.DataFrame(main)
    df.to_csv("tables/benchmark-list.csv")

#    df_list = []
#    for bmark, tags in tags_taggroups.items():
#        print(bmark)
#        print(tags)
#        #df_list.append(tags)
#        print(tags_benchmark_map[bmark])
#        print("")
#

    #df = pd.DataFrame(df_list, columns=benchmarks)
    #print(df)

    #for i in benchmarks:
    #    application_file = "../repo/%s/application.py" % i
    #    if os.path.exists(application_file):
    #        with open(application_file) as f:
    #            for line in f.readlines():
    #                if re.search(r'tags = \[', line):
    #                    print(line)

    #df2 = pd.DataFrame({
    #    "tag group": pd.Series(tag_groups),
    #})
    #res = df2.join(df)
    #print(res)

    #################
    # Tables
    # columns: benchmarks (i.e., amg2023)
    # rows: tag groups (i.e., application domain).  Each cell should hopefully have a tag - and some might have multiple


if __name__ == "__main__":
    try:
        workspace = sys.argv[1]
    except IndexError:
        print("Usage: " + os.path.basename(__file__) + " <workspace>")
        sys.exit(1)

    main(workspace)
