#!/usr/bin/env python3

import pandas as pd
import yaml
import os

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


def join_dicts(dict1, dict2):
    print(dict1)
    print(dict2)
    return(dict2.update(dict1))


def main():
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

    df_list = []

    print("Tags in benchpark_tags:")
    for k, v in tag_dicts.items():
        benchmarks_dict = {}
        for i in benchmarks:
            benchmarks_dict[i] = [""] * len(v)

        d = {"": v}
        x = {**d, **benchmarks_dict}
        tmp_df = pd.DataFrame(x)
        df_list.append(tmp_df)
        print(tmp_df)

    #print("\n")


    #################
    # Tables for each "tag group" (i.e., application domain), "tag group" becomes the name of the table
    # columns: benchmarks.  The columns should be the same for all tables
    # rows: tags in the tag group. 




if __name__ == "__main__":
    main()
