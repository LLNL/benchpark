# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import collections.abc
import inspect
import os
import re
from typing import Any, Callable, Dict, Optional, Tuple, Union
import yaml  # TODO: some way to ensure yaml available

from benchpark.directives import SpecTemplate
import benchpark.spec
import benchpark.paths
import benchpark.repo
import benchpark.runtime
import benchpark.variant

import ramble.language.language_base
import ramble.language.language_helpers
import ramble.language.shared_language
from ramble.language.language_base import DirectiveError

bootstrapper = benchpark.runtime.RuntimeResources(benchpark.paths.benchpark_home)
bootstrapper.bootstrap()


class Experiment(SpecTemplate):
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
