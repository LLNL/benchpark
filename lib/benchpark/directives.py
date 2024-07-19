# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0
import collections.abc
import functools
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set, Tuple, Union
import re

import llnl.util.lang
import benchpark.spec
import benchpark.variant

"""This package contains directives that can be used within an experiment.

Directives are functions that can be called inside an experiment
definition to modify the package, for example:

    class OpenMpi(Experiment):
        variant("ranks")
        ...

``variant`` is a benchpark directive.

The available directives are:

  * ``variant``

"""

__all__ = [
    "DirectiveError",
    "DirectiveMeta",
    "variant",
]

#: Names of possible directives. This list is mostly populated using the @directive decorator.
#: Some directives leverage others and in that case are not automatically added.
directive_names = []


class DirectiveMeta(type):
    """Flushes the directives that were temporarily stored in the staging
    area into the package.
    """

    # Set of all known directives
    _directive_dict_names: Set[str] = set()
    _directives_to_be_executed: List[str] = []
    _default_args: List[dict] = []

    def __new__(cls, name, bases, attr_dict):
        # Initialize the attribute containing the list of directives
        # to be executed. Here we go reversed because we want to execute
        # commands:
        # 1. in the order they were defined
        # 2. following the MRO
        attr_dict["_directives_to_be_executed"] = []
        for base in reversed(bases):
            try:
                directive_from_base = base._directives_to_be_executed
                attr_dict["_directives_to_be_executed"].extend(directive_from_base)
            except AttributeError:
                # The base class didn't have the required attribute.
                # Continue searching
                pass

        # De-duplicates directives from base classes
        attr_dict["_directives_to_be_executed"] = [
            x for x in llnl.util.lang.dedupe(attr_dict["_directives_to_be_executed"])
        ]

        # Move things to be executed from module scope (where they
        # are collected first) to class scope
        if DirectiveMeta._directives_to_be_executed:
            attr_dict["_directives_to_be_executed"].extend(
                DirectiveMeta._directives_to_be_executed
            )
            DirectiveMeta._directives_to_be_executed = []

        return super(DirectiveMeta, cls).__new__(cls, name, bases, attr_dict)

    def __init__(cls, name, bases, attr_dict):
        # The instance is being initialized: if it is an experiment we must ensure
        # that the directives are called to set it up.
        if "benchpark.expr" in cls.__module__:
            # Ensure the presence of the dictionaries associated with the directives.
            # All dictionaries are defaultdicts that create lists for missing keys.
            for d in DirectiveMeta._directive_dict_names:
                setattr(cls, d, {})

            # Lazily execute directives
            for directive in cls._directives_to_be_executed:
                directive(cls)

            # Ignore any directives executed *within* top-level
            # directives by clearing out the queue they're appended to
            DirectiveMeta._directives_to_be_executed = []

        super(DirectiveMeta, cls).__init__(name, bases, attr_dict)

    @staticmethod
    def push_default_args(default_args):
        """Push default arguments"""
        DirectiveMeta._default_args.append(default_args)

    @staticmethod
    def pop_default_args():
        """Pop default arguments"""
        return DirectiveMeta._default_args.pop()

    @staticmethod
    def directive(dicts=None):
        """Decorator for Benchpark directives.

        Benchpark directives allow you to modify an experiment while it is being
        defined, e.g. to add a variant.  Directives
        are one of the key pieces of Benchpark's experiment "language", which is
        embedded in python.

        Here's an example directive:

        .. code-block:: python

            @directive(dicts='variant')
            variant(expr, ...):
                ...

        This directive allows you write:

        .. code-block:: python

            class Foo(Experiment):
                variant(...)

        The ``@directive`` decorator handles a couple things for you:

          1. Adds the class scope (expr) as an initial parameter when
             called, like a class method would.  This allows you to modify
             an experiment from within a directive, while the package is still
             being defined.

          2. It automatically adds a dictionary called "variants" to the
             experiment so that you can refer to expr.variants.

        The ``(dicts='variant')`` part ensures that ALL experiments in Benchpark
        will have a ``variants`` attribute after they're constructed, and
        that if no directive actually modified it, it will just be an
        empty dict.

        This is just a modular way to add storage attributes to the
        Experiment class, and it's how Benchpark gets information from the
        experiments to the core.
        """
        global directive_names

        if isinstance(dicts, str):
            dicts = (dicts,)

        if not isinstance(dicts, collections.abc.Sequence):
            message = "dicts arg must be list, tuple, or string. Found {0}"
            raise TypeError(message.format(type(dicts)))

        # Add the dictionary names if not already there
        DirectiveMeta._directive_dict_names |= set(dicts)

        # This decorator just returns the directive functions
        def _decorator(decorated_function):
            directive_names.append(decorated_function.__name__)

            @functools.wraps(decorated_function)
            def _wrapper(*args, **_kwargs):
                # First merge default args with kwargs
                kwargs = dict()
                for default_args in DirectiveMeta._default_args:
                    kwargs.update(default_args)
                kwargs.update(_kwargs)

                # # Inject when arguments from the context
                # if DirectiveMeta._when_constraints_from_context:
                #     # Check that directives not yet supporting the when= argument
                #     # are not used inside the context manager
                #     if decorated_function.__name__ == "version":
                #         msg = (
                #             'directive "{0}" cannot be used within a "when"'
                #             ' context since it does not support a "when=" '
                #             "argument"
                #         )
                #         msg = msg.format(decorated_function.__name__)
                #         raise DirectiveError(msg)

                # If any of the arguments are executors returned by a
                # directive passed as an argument, don't execute them
                # lazily. Instead, let the called directive handle them.
                # This allows nested directive calls in packages.  The
                # caller can return the directive if it should be queued.
                def remove_directives(arg):
                    directives = DirectiveMeta._directives_to_be_executed
                    if isinstance(arg, (list, tuple)):
                        # Descend into args that are lists or tuples
                        for a in arg:
                            remove_directives(a)
                    else:
                        # Remove directives args from the exec queue
                        remove = next((d for d in directives if d is arg), None)
                        if remove is not None:
                            directives.remove(remove)

                # Nasty, but it's the best way I can think of to avoid
                # side effects if directive results are passed as args
                remove_directives(args)
                remove_directives(list(kwargs.values()))

                # A directive returns either something that is callable on a
                # package or a sequence of them
                result = decorated_function(*args, **kwargs)

                # ...so if it is not a sequence make it so
                values = result
                if not isinstance(values, collections.abc.Sequence):
                    values = (values,)

                DirectiveMeta._directives_to_be_executed.extend(values)

                # wrapped function returns same result as original so
                # that we can nest directives
                return result

            return _wrapper

        return _decorator


SubmoduleCallback = Callable[
    ["benchpark.experiment.Experiment"], Union[str, List[str], bool]
]
directive = DirectiveMeta.directive


@directive("variants")
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


class DirectiveError(benchpark.error.BenchparkError):
    """This is raised when something is wrong with a package directive."""
