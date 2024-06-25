# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, Tuple
import os
import inspect

import benchpark.directives
import benchpark.repo
from llnl.util.lang import classproperty, memoized


class ExperimentMeta(
    benchpark.directives.DirectiveMeta,
):
    """
    Package metaclass for supporting directives (e.g., depends_on) and phases
    """

    def __new__(cls, name, bases, attr_dict):
        """
        FIXME: REWRITE
        Instance creation is preceded by phase attribute transformations.

        Conveniently transforms attributes to permit extensible phases by
        iterating over the attribute 'phases' and creating / updating private
        InstallPhase attributes in the class that will be initialized in
        __init__.
        """
        attr_dict["_name"] = None

        return super(ExperimentMeta, cls).__new__(cls, name, bases, attr_dict)


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
    variants: Dict[str, Tuple["benchpark.variant.Variant", "benchpark.experiment_spec.ConcreteSpec"]]

    def __init__(self, spec):
        self.spec: "benchpark.experiment_spec.ConcreteSpec" = spec
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
        return benchpark.repo.namespace_from_fullname(cls.__module__)

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
        if isinstance(self.spec, benchpark.experiment_spec.ConcreteSpec):
            return None
        else:
            # If it's not concrete, then return the spec from the
            # extends() directive since that is all we know so far.
            spec_str = next(iter(self.extendees))
            return benchpark.experiment_spec.Spec(spec_str)

    @property
    def is_extension(self):
        # if it is concrete, it's only an extension if it actually
        # dependes on the extendee.
        if isinstance(self.spec, benchpark.experiment_spec.ConcreteSpec):
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
