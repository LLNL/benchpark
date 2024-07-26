# SPDX-License-Identifier: Apache-2.0

import hashlib
import importlib.util
import os
import pathlib
import sys

import benchpark.paths
from benchpark.runtime import RuntimeResources

# isort: off

bootstrapper = RuntimeResources(benchpark.paths.benchpark_home)  # noqa
bootstrapper.bootstrap()  # noqa

import ramble.config as cfg  # noqa
import spack.util.spack_yaml as syaml  # noqa

# isort: on

# We cannot import this the normal way because it from modern Spack
# and mixing modern Spack modules with ramble modules that depend on
# ancient Spack will cause errors. This module is safe to load as an
# individual because it is not used by Ramble
# The following code block implements the line
# import spack.schema.packages as packages_schema
packages_schema_spec = importlib.util.spec_from_file_location(
    "spack.schema.packages",
    f"{bootstrapper.spack_location}/lib/spack/spack/schema/packages.py",
)
packages_schema = importlib.util.module_from_spec(packages_schema_spec)
sys.modules["spack.schema.packages"] = packages_schema
packages_schema_spec.loader.exec_module(packages_schema)


def _hash_id(content_list):
    sha256_hash = hashlib.sha256()
    for x in content_list:
        sha256_hash.update(x.encode("utf-8"))
    return sha256_hash.hexdigest()


class System:
    def __init__(self):
        self.external_resources = None

        self.sys_cores_per_node = None
        self.sys_gpus_per_node = None
        self.sys_mem_per_node = None
        self.scheduler = None
        self.timeout = "120"
        self.queue = None

        self.required = ["sys_cores_per_node", "scheduler", "timeout"]

    def generate_description(self, output_dir):
        output_dir = pathlib.Path(output_dir)

        variables_yaml = output_dir / "variables.yaml"
        with open(variables_yaml, "w") as f:
            f.write(self.variables_yaml())

        self.externals(output_dir)

    def system_id(self):
        return _hash_id([self.variables_yaml()])

    def externals(self, output_dir):
        if not self.external_resources:
            return

        # Each subdir of external-resources contains a mutually-exclusive
        # set of package files
        selections = list()
        for component in os.listdir(self.external_resources):
            component_dir = self.external_resources / component
            component_choices = list(sorted(os.listdir(component_dir)))
            # TODO: for now, pick the first; need to allow users to select
            selections.append(component_dir / component_choices[0])

        data = cfg.read_config_file(selections[0], packages_schema.schema)
        for selection in selections[1:]:
            cfg.merge_yaml(
                data, cfg.read_config_file(selection, packages_schema.schema)
            )

        aux = output_dir / "auxiliary_software_files"
        os.mkdir(aux)

        aux_packages = aux / "packages.yaml"
        with open(aux_packages, "w") as outstream:
            syaml.dump_config(data, outstream)

    def variables_yaml(self):
        for attr in self.required:
            if not getattr(self, attr, None):
                raise ValueError(f"Missing required info: {attr}")

        optionals = list()
        for opt in ["sys_gpus_per_node", "sys_mem_per_node", "queue"]:
            if getattr(self, opt, None):
                optionals.append(f"{opt}: {getattr(self, opt)}")
        indent = " " * 2
        if optionals:
            optionals_as_cfg = f"\n{indent}".join(optionals)
        return f"""\
# SPDX-License-Identifier: Apache-2.0

variables:
  timeout: "{self.timeout}"
  scheduler: "{self.scheduler}"
  sys_cores_per_node: "{self.sys_cores_per_node}"
  {optionals_as_cfg}
  max_request: "1000"  # n_ranks/n_nodes cannot exceed this
  n_ranks: '1000001'  # placeholder value
  n_nodes: '1000001'  # placeholder value
  batch_submit: "placeholder"
  mpi_command: "placeholder"
"""
