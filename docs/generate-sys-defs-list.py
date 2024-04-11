#!/usr/bin/env python3

import glob

import pandas as pd
import yaml


def main():
    sysconfig_yaml_files = glob.glob(
        "../configs/**/system_definition.yaml", recursive=True
    )

    df_list = []
    for f in sysconfig_yaml_files:
        with open(f, "r") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

            tmp_df = pd.json_normalize(data, max_level=2)
            df_list.append(tmp_df)

    df = pd.concat(df_list)

    # Data formatting: converts system-tested.description yaml value to rst
    # format for external links
    df.loc[
        df["system_definition.system-tested.description"].notna(),
        "system_definition.system-tested.description",
    ] = (
        "`"
        + df.loc[
            df["system_definition.system-tested.description"].notna(),
            "system_definition.system-tested.description",
        ].astype(str)
        + "`_"
    )

    # Data formatting: converts top500-system-instances yaml list to rst string
    # of strings (ideally to put 1 per line)
    list_of_strings = []
    for i in df["system_definition.top500-system-instances"]:
        list_of_strings.append(", ".join(item for item in i if item))
    df.loc[:, "system_definition.top500-system-instances"] = list_of_strings

    # Set index to be system names
    df.set_index("system_definition.name", inplace=True)
    df.index.name = ""  # remove system_definition.name from cell
    df_tpose = df.T

    # Remove system_definition from all field names
    # (e.g., system_definition.system-tested.description)
    df_tpose["fielddesc"] = df_tpose.index
    df_tpose[["first", ""]] = df_tpose["fielddesc"].str.split(".", n=1, expand=True)

    # Add ** to either side of field names for bold rendering in RST
    df_tpose[""] = "**" + df_tpose[""] + "**"

    # Drop temporary columns
    df_tpose.drop(["first", "fielddesc"], axis=1, inplace=True)

    # Replace NaN with empty string
    df_tpose.fillna("", inplace=True)

    # Set index to be field names
    df_tpose.set_index([""], inplace=True)

    # Write out current system definitions to CSV format
    df_tpose.to_csv("current-system-definitions.csv")


if __name__ == "__main__":
    main()
