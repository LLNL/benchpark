# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import collections.abc
import functools
import inspect
import os
import re
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple, Union
import yaml  # TODO: some way to ensure yaml available

import benchpark.spec
import benchpark.paths
import benchpark.repo
import benchpark.runtime
import benchpark.variant

bootstrapper = benchpark.runtime.RuntimeResources(benchpark.paths.benchpark_home)
bootstrapper.bootstrap()

from llnl.util.lang import memoized
import ramble.language.language_base
import ramble.language.language_helpers
import ramble.language.shared_language
from ramble.language.language_base import DirectiveError


#### TODO remove this when it is added to ramble.lang (when ramble updates from spack
class classproperty:
    """Non-data descriptor to evaluate a class-level property. The function that performs
    the evaluation is injected at creation time and take an instance (could be None) and
    an owner (i.e. the class that originated the instance)
    """

    def __init__(self, callback):
        self.callback = callback

    def __get__(self, instance, owner):
        return self.callback(owner)


class ExperimentMeta(ramble.language.shared_language.SharedMeta):
    """
    Package metaclass for supporting directives (e.g., depends_on) and phases
    """

    _directive_names = set()
    _directives_to_be_executed = []

    # Hack to be able to use SharedMeta outside of Ramble
    # will ask Ramble to implement fix on their end and then we can remove this
    def __init__(self, *args, **kwargs):
        with benchpark.repo.override_ramble_hardcoded_globals():
            super(ExperimentMeta, self).__init__(*args, **kwargs)


experiment_directive = ExperimentMeta.directive


@experiment_directive("variants")
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
    """Define a variant for the experiment.

    Experimentizer can specify a default value as well as a text description.

    Args:
        name: Name of the variant
        default: Default value for the variant, if not specified otherwise the default will be
            False for a boolean variant and 'nothing' for a multi-valued variant
        description: Description of the purpose of the variant
        values: Either a tuple of strings containing the allowed values, or a callable accepting
            one value and returning True if it is valid
        multi: If False only one value per spec is allowed for this variant
        validator: Optional group validator to enforce additional logic. It receives the experiment
            name, the variant name and a tuple of values and should raise an instance of BenchparkError
            if the group doesn't meet the additional constraints
        when: Optional condition on which the variant applies
        sticky: The variant should not be changed by the concretizer to find a valid concrete spec

    Raises:
        DirectiveError: If arguments passed to the directive are invalid
    """

    def format_error(msg, pkg):
        msg += " @*r{{[{0}, variant '{1}']}}"
        return msg.format(pkg.name, name)

    # Ensure we have a sequence of allowed variant values, or a
    # predicate for it.
    if values is None:
        if str(default).upper() in ("TRUE", "FALSE"):
            values = (True, False)
        else:
            values = lambda x: True

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


class Experiment(metaclass=ExperimentMeta):
    """This is the superclass for all benchpark experiments.

    ***The Experiment class***

    Experiments are written in pure Python.

    There are two main parts of a Benchpark experiment:

      1. **The experiment class**.  Classes contain ``directives``, which are
         special functions, that add metadata (variants) to packages (see
         ``directives.py``).

      2. **Experiment instances**. Once instantiated, a package is
         essentially a software installer.  Spack calls methods like
         ``do_install()`` on the ``Package`` object, and it uses those to
         drive user-implemented methods like ``patch()``, ``install()``, and
         other build steps.  To install software, an instantiated package
         needs a *concrete* spec, which guides the behavior of the various
         install methods.

    Experiments are imported from repos (see ``repo.py``).

    **Package DSL**

    Look in ``lib/spack/docs`` or check https://spack.readthedocs.io for
    the full documentation of the package domain-specific language.  That
    used to be partially documented here, but as it grew, the docs here
    became increasingly out of date.

    **Package Lifecycle**

    A package's lifecycle over a run of Spack looks something like this:

    .. code-block:: python

       p = Package()             # Done for you by spack

       p.do_fetch()              # downloads tarball from a URL (or VCS)
       p.do_stage()              # expands tarball in a temp directory
       p.do_patch()              # applies patches to expanded source
       p.do_install()            # calls package's install() function
       p.do_uninstall()          # removes install directory

    although packages that do not have code have nothing to fetch so omit
    ``p.do_fetch()``.

    There are also some other commands that clean the build area:

    .. code-block:: python

       p.do_clean()              # removes the stage directory entirely
       p.do_restage()            # removes the build directory and
                                 # re-expands the archive.

    The convention used here is that a ``do_*`` function is intended to be
    called internally by Spack commands (in ``spack.cmd``).  These aren't for
    package writers to override, and doing so may break the functionality
    of the Package class.

    Package creators have a lot of freedom, and they could technically
    override anything in this class.  That is not usually required.

    For most use cases.  Package creators typically just add attributes
    like ``homepage`` and, for a code-based package, ``url``, or functions
    such as ``install()``.
    There are many custom ``Package`` subclasses in the
    ``spack.build_systems`` package that make things even easier for
    specific build systems.

    """

    #
    # These are default values for instance variables.
    #

    # This allows analysis tools to correctly interpret the class attributes.
    variants: Dict[
        str,
        Tuple["benchpark.variant.Variant", "benchpark.spec.ConcreteExperimentSpec"],
    ]

    def __init__(self, spec):
        self.spec: "benchpark.spec.ConcreteExperimentSpec" = spec
        super().__init__()

    @classproperty
    def package_dir(cls):
        """Directory where the package.py file lives."""
        return os.path.abspath(os.path.dirname(cls.module.__file__))

    @classproperty
    def module(cls):
        """Module object (not just the name) that this package is defined in.

        We use this to add variables to package modules.  This makes
        install() methods easier to write (e.g., can call configure())
        """
        return __import__(cls.__module__, fromlist=[cls.__name__])

    @classproperty
    def namespace(cls):
        """Spack namespace for the package, which identifies its repo."""
        parts = cls.__module__.split(".")
        return ".".join(parts[2:-1])

    @classproperty
    def fullname(cls):
        """Name of this package, including the namespace"""
        return f"{cls.namespace}.{cls.name}"

    @classproperty
    def fullnames(cls):
        """Fullnames for this package and any packages from which it inherits."""
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
        """The name of this package.

        The name of a package is the name of its Python module, without
        the containing module names.
        """
        if cls._name is None:
            cls._name = cls.module.__name__
            if "." in cls._name:
                cls._name = cls._name[cls._name.rindex(".") + 1 :]
        return cls._name

    # TODO: allow more than one active extendee.
    @property
    def extendee_spec(self):
        """
        Spec of the extendee of this package, or None if it is not an extension
        """
        if not self.extendees:
            return None

        # if the spec is concrete already, then it extends something
        # that is an *optional* dependency, and the dep isn't there.
        if isinstance(self.spec, benchpark.spec.ConcreteSpec):
            return None
        else:
            # If it's not concrete, then return the spec from the
            # extends() directive since that is all we know so far.
            spec_str = next(iter(self.extendees))
            return benchpark.spec.Spec(spec_str)

    @property
    def is_extension(self):
        # if it is concrete, it's only an extension if it actually
        # dependes on the extendee.
        if isinstance(self.spec, benchpark.spec.ConcreteSpec):
            return self.extendee_spec is not None
        else:
            # If not, then it's an extension if it *could* be an extension
            return bool(self.extendees)

    def extends(self, spec):
        """
        Returns True if this package extends the given spec.

        If ``self.spec`` is concrete, this returns whether this package extends
        the given spec.

        If ``self.spec`` is not concrete, this returns whether this package may
        extend the given spec.
        """
        if spec.name not in self.extendees:
            return False
        s = self.extendee_spec
        return s and spec.satisfies(s)

    def compute_include_section(self):
        # include the config directory
        # TODO: does this need to change to interop with System class
        return ["./configs"]

    def compute_config_section(self):
        # default configs for all experiments
        return {
            "deprecated": True,
            "spack_flags": {"install": "--add --keep-stage", "concretize": "-U -f"},
        }

    def compute_modifiers_section(self):
        # by default we use the allocation modifier and no others
        return [{"name": "allocation"}]

    def compute_applications_section(self):
        # TODO: is there some reasonable default?
        raise NotImplementedError(
            "Each experiment must implement compute_applications_section"
        )

    def compute_spack_section(self):
        # TODO: is there some reasonable default based on known variable names?
        raise NotImplementedError(
            "Each experiment must implement compute_spack_section"
        )

    def compute_ramble_dict(self):
        # This can be overridden by any subclass that needs more flexibility
        return {
            "ramble": {
                "include": self.compute_include_section(),
                "config": self.compute_config_section(),
                "modifiers": self.compute_modifiers_section(),
                "applications": self.compute_applications_section(),
                "spack": self.compute_spack_section(),
            }
        }

    def write_ramble_dict(self, filepath):
        ramble_dict = self.compute_ramble_dict()
        with open(filepath, "w") as f:
            yaml.dump(ramble_dict, f)
