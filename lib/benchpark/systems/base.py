# SPDX-License-Identifier: Apache-2.0

import pathlib

from benchpark.runtime import RuntimeResources


class ScriptResources(RuntimeResources):
    def __init__(self):
        script_resource_root = pathlib.Path(os.path.abspath(__module__.__file__)).parents[3] / "external-resources"
        super().__init__(script_resource_root)


class SpackConfigMergeResolver:
    def __init__(self, benchpark_installation):
        self.benchpark_installation = benchpark_installation
        self.script = benchpark_installation.root / "lib" / "scripts" / "merge.py"
        self.ramble = None

    def prepare(self):
        self.spack = self.benchpark_installation.spack()

    def __call__(self, path1, path2):
        """Merge config from path1 into path2"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)

            merged_config = temp_dir / pathlib.Path(path2).name

            run_command(
                f"{self.spack} python {self.script} {path1} {path2} {merged_config}"
            )

            debug_print(f"Overwrite {path2} with merged yaml from {merged_config}")
            # Overwrite the destination path with the merged result
            shutil.copy2(merged_config, path2)


class System:
    def __init__(self, input_dir):
        self.sys_cores_per_node = None
        self.sys_gpus_per_node = None
        self.sys_mem_per_node = None
        self.scheduler = None
        self.timeout = "120"
        self.queue = None

        self.required = ["sys_cores_per_node", "scheduler", "timeout"]

    def generate_description(self, output_dir):
        variables_yaml = output_dir / "variables.yaml"
        with open(variables_yaml, "w") as f:
            f.write(self.variables_yaml())

    def externals(self, destdir):
        # Each subdir of auxiliary_packages contains a set of mutually-exclusive
        # configs. If the user specified nothing, we can combine the "first"
        # file from each directory into a single packages config.
        # (you can sort them alphabetically, choosing names like 01-rocm-543.yaml)
        pass

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
