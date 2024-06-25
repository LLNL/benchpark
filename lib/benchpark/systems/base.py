# SPDX-License-Identifier: Apache-2.0

import hashlib
import os
import pathlib
import shutil
import tempfile

from benchpark.runtime import RuntimeResources


def _hash_id(content_list):
    sha256_hash = hashlib.sha256()
    for x in content_list:
        sha256_hash.update(x.encode("utf-8"))
    return sha256_hash.hexdigest()


_scripts_basedir = pathlib.Path(os.path.abspath(__file__)).parents[3] / "script-resources"


class ScriptResources(RuntimeResources):
    def __init__(self):
        super().__init__(_scripts_basedir)


class SpackConfigMergeResolver:
    def __init__(self, script_resources):
        self.script_resources = script_resources
        self.merge_script = _scripts_basedir / "merge-spack-config.py"

    def __call__(self, path1, path2):
        """Merge config from path1 into path2"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)

            merged_config = temp_dir / pathlib.Path(path2).name

            spack = self.script_resources.spack()
            spack(
                f"python {self.merge_script} {path1} {path2} {merged_config}"
            )

            # Overwrite the destination path with the merged result
            shutil.copy2(merged_config, path2)


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

        # Now we have a set of packages.yaml files we need to merge together
        merge = SpackConfigMergeResolver(ScriptResources())

        aux = output_dir / "auxiliary_software_files"
        os.mkdir(aux)
        aux_packages = aux / "packages.yaml"
        shutil.copy2(selections[0], aux_packages)
        for selection in selections[1:]:
            merge(selection, aux_packages)

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
