#!/usr/bin/env python3

import pandas as pd
import yaml
import os
import re


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


def main():
    benchmarks = list()
    benchpark_benchmarks(benchmarks)

    for i in benchmarks:
        application_file = "../repo/%s/application.py" % i
        if os.path.exists(application_file):
            with open(application_file) as f:
                for line in f.readlines():
                    if re.search(r'tags = \[', line):
                        print(line)

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

    df = pd.DataFrame({
        #"benchmarks": benchmarks,
        "tag group": tag_dicts.keys(),
    })
    print(df)

    #################
    # Tables
    # rows: benchmarks (i.e., amg2023)
    # columns: tag groups (i.e., application domain).  Each cell should hopefully have a tag - and some might have multiple


if __name__ == "__main__":
    main()
