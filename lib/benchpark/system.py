# SPDX-License-Identifier: Apache-2.0

import hashlib
import importlib.util
import os
import pathlib
import sys

import benchpark.paths
import benchpark.repo
from benchpark.runtime import RuntimeResources

# Duplicate imports from experiment.py
import collections.abc
import inspect
import re
from typing import Any, Callable, Dict, Optional, Tuple, Union
import yaml  # TODO: some way to ensure yaml available
import benchpark.spec
import benchpark.variant
import ramble.language.language_base
import ramble.language.language_helpers
import ramble.language.shared_language
from ramble.language.language_base import DirectiveError

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
schemas = {
    "spack.schema.packages": f"{bootstrapper.spack_location}/lib/spack/spack/schema/packages.py",
    "spack.schema.compilers": f"{bootstrapper.spack_location}/lib/spack/spack/schema/compilers.py",
}

def load_schema(schema_id, schema_path):
    schema_spec = importlib.util.spec_from_file_location(
        schema_id, schema_path
    )
    schema = importlib.util.module_from_spec(schema_spec)
    sys.modules[schema_id] = schema
    schema_spec.loader.exec_module(schema)
    return schema

packages_schema = load_schema(
    "spack.schema.packages",
    f"{bootstrapper.spack_location}/lib/spack/spack/schema/packages.py",
)
compilers_schema = load_schema(
    "spack.schema.compilers",
    f"{bootstrapper.spack_location}/lib/spack/spack/schema/compilers.py",
)


_repo_path = benchpark.repo.paths[benchpark.repo.ObjectTypes.systems]


# Duplicated from experiment.py
class classproperty:
    """Non-data descriptor to evaluate a class-level property. The function that performs
    the evaluation is injected at creation time and take an instance (could be None) and
    an owner (i.e. the class that originated the instance)
    """

    def __init__(self, callback):
        self.callback = callback

    def __get__(self, instance, owner):
        return self.callback(owner)


class SystemMeta(ramble.language.shared_language.SharedMeta):
    _directive_names = set()
    _directives_to_be_executed = []

    # Hack to be able to use SharedMeta outside of Ramble
    # will ask Ramble to implement fix on their end and then we can remove this
    def __init__(self, *args, **kwargs):
        with benchpark.repo.override_ramble_hardcoded_globals():
            super(SystemMeta, self).__init__(*args, **kwargs)


system_directive = SystemMeta.directive


@system_directive("variants")
def variant(
    name: str,
    default: Optional[Any] = None,
    description: str = "",
    values: Optional[Union[collections.abc.Sequence, Callable[[Any], bool]]] = None,
    multi: Optional[bool] = None,
    validator: Optional[Callable[[str, str, Tuple[Any, ...]], None]] = None,
    when: Optional[Union[str, bool]] = None,
    sticky: bool = False,
):
    def format_error(msg, pkg):
        msg += " @*r{{[{0}, variant '{1}']}}"
        return msg.format(pkg.name, name)

    def _always_true(_x):
        return True

    # Ensure we have a sequence of allowed variant values, or a
    # predicate for it.
    if values is None:
        if str(default).upper() in ("TRUE", "FALSE"):
            values = (True, False)
        else:
            values = _always_true

    # The object defining variant values might supply its own defaults for
    # all the other arguments. Ensure we have no conflicting definitions
    # in place.
    for argument in ("default", "multi", "validator"):
        # TODO: we can consider treating 'default' differently from other
        # TODO: attributes and let a packager decide whether to use the fluent
        # TODO: interface or the directive argument
        if hasattr(values, argument) and locals()[argument] is not None:

            def _raise_argument_error(pkg):
                msg = (
                    "Remove specification of {0} argument: it is handled "
                    "by an attribute of the 'values' argument"
                )
                raise DirectiveError(format_error(msg.format(argument), pkg))

            return _raise_argument_error

    # Allow for the object defining the allowed values to supply its own
    # default value and group validator, say if it supports multiple values.
    default = getattr(values, "default", default)
    validator = getattr(values, "validator", validator)
    multi = getattr(values, "multi", bool(multi))

    # Here we sanitize against a default value being either None
    # or the empty string, as the former indicates that a default
    # was not set while the latter will make the variant unparsable
    # from the command line
    if default is None or default == "":

        def _raise_default_not_set(pkg):
            if default is None:
                msg = "either a default was not explicitly set, or 'None' was used"
            elif default == "":
                msg = "the default cannot be an empty string"
            raise DirectiveError(format_error(msg, pkg))

        return _raise_default_not_set

    description = str(description).strip()

    def _execute_variant(pkg):
        if not re.match(benchpark.spec.IDENTIFIER, name):
            directive = "variant"
            msg = "Invalid variant name in {0}: '{1}'"
            raise DirectiveError(directive, msg.format(pkg.name, name))

        pkg.variants[name] = benchpark.variant.Variant(
            name, default, description, values, multi, validator, sticky
        )

    return _execute_variant
# end duplication from experiment.py


def system_class(system_id):
    cls = _repo_path.get_obj_class(system_id)
    loc = pathlib.Path(_repo_path.filename_for_object_name(system_id)).parent
    setattr(cls, "resource_location", loc)
    return cls


def _hash_id(content_list):
    sha256_hash = hashlib.sha256()
    for x in content_list:
        sha256_hash.update(x.encode("utf-8"))
    return sha256_hash.hexdigest()


class System(metaclass=SystemMeta):
    variants: Dict[
        str,
        Tuple["benchpark.variant.Variant", "benchpark.spec.ConcreteSystemSpec"],
    ]

    def __init__(self, spec):
        self.spec: "benchpark.spec.ConcreteSystemSpec" = spec
        super().__init__()

    @classproperty
    def package_dir(cls):
        return os.path.abspath(os.path.dirname(cls.module.__file__))

    @classproperty
    def module(cls):
        return __import__(cls.__module__, fromlist=[cls.__name__])

    @classproperty
    def namespace(cls):
        parts = cls.__module__.split(".")
        return ".".join(parts[2:-1])

    @classproperty
    def fullname(cls):
        return f"{cls.namespace}.{cls.name}"

    @classproperty
    def fullnames(cls):
        fullnames = []
        for cls in inspect.getmro(cls):
            namespace = getattr(cls, "namespace", None)
            if namespace:
                fullnames.append(f"{namespace}.{cls.name}")
            if namespace == "builtin":
                # builtin packages cannot inherit from other repos
                break
        return fullnames

    @classproperty
    def name(cls):
        if cls._name is None:
            cls._name = cls.module.__name__
            if "." in cls._name:
                cls._name = cls._name[cls._name.rindex(".") + 1 :]
        return cls._name

    def initialize(self):
        self.external_resources = None

        self.sys_cores_per_node = None
        self.sys_gpus_per_node = None
        self.sys_mem_per_node = None
        self.scheduler = None
        self.timeout = "120"
        self.queue = None

        self.required = ["sys_cores_per_node", "scheduler", "timeout"]

    def generate_description(self, output_dir):
        self.initialize()
        output_dir = pathlib.Path(output_dir)

        variables_yaml = output_dir / "variables.yaml"
        with open(variables_yaml, "w") as f:
            f.write(self.variables_yaml())

        self.external_packages(output_dir)
        self.compilers(output_dir)

        system_id_path = output_dir / "system_id.yaml"
        with open(system_id_path, "w") as f:
            f.write(f"""\
system:
  name: {self.__class__.__name__}
""")

    def system_id(self):
        return _hash_id([self.variables_yaml()])

    def _merge_config_files(self, schema, selections, dst_path):
        data = cfg.read_config_file(selections[0], schema)
        for selection in selections[1:]:
            cfg.merge_yaml(
                data, cfg.read_config_file(selection, schema)
            )

        with open(dst_path, "w") as outstream:
            syaml.dump_config(data, outstream)

    def _select_components(self, basedir):
        """Each subdir of `basedir` contains a mutually-exclusive set of
        files: select one file from each component subdir.
        """
        selections = list()
        for component in os.listdir(basedir):
            component_dir = basedir / component
            component_choices = list(sorted(os.listdir(component_dir)))
            # TODO: for now, pick the first; need to allow users to select
            selections.append(component_dir / component_choices[0])

        return selections

    def external_packages(self, output_dir):
        pkgs_basedir = pathlib.Path(self.resource_location) / "externals"
        if not pkgs_basedir.exists():
            return

        selections = self._select_components(pkgs_basedir)

        aux = output_dir / "auxiliary_software_files"
        os.makedirs(aux, exist_ok=True)
        aux_packages = aux / "packages.yaml"

        self._merge_config_files(packages_schema.schema, selections, aux_packages)

    def compilers(self, output_dir):
        compilers_basedir = pathlib.Path(self.resource_location) / "compilers"
        if not compilers_basedir.exists():
            return

        selections = self._select_components(compilers_basedir)

        aux = output_dir / "auxiliary_software_files"
        os.makedirs(aux, exist_ok=True)
        aux_compilers = aux / "compilers.yaml"

        self._merge_config_files(compilers_schema.schema, selections, aux_compilers)

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
