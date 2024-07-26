# Copyright 2022-2024 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import os
import sys
import functools
import contextlib

from enum import Enum

import benchpark.paths
import benchpark.runtime
import benchpark.spec

# Need to retrieve Ramble to import it
# isort: off
bootstrapper = benchpark.runtime.RuntimeResources(benchpark.paths.benchpark_home)
bootstrapper.bootstrap()

import llnl.util.lang
import ramble.language.language_base
import ramble.repository

# isort: on

global_namespace = "benchpark"
namespaces = ["benchpark.expr"]

#: Guaranteed unused default value for some functions.
NOT_PROVIDED = object()


####
# Implement type specific functionality between here, and
#     END TYPE SPECIFIC FUNCTIONALITY
####
ObjectTypes = Enum("ObjectTypes", ["experiments"])

OBJECT_NAMES = [obj.name for obj in ObjectTypes]

default_type = ObjectTypes.experiments

type_definitions = {
    ObjectTypes.experiments: {
        "file_name": "experiment.py",
        "dir_name": "experiments",
        "abbrev": "expr",
        "config_section": "repos",
        "accepted_configs": ["repo.yaml"],
        "singular": "experiment",
    },
}


@contextlib.contextmanager
def override_ramble_hardcoded_globals():
    _old = (
        ramble.repository.type_definitions,
        ramble.repository.global_namespace,
        ramble.language.language_base.namespaces,
    )
    ramble.repository.type_definitions = type_definitions
    ramble.repository.global_namespace = global_namespace
    ramble.language.language_base.namespaces = namespaces

    yield

    ramble.repository.type_definitions = _old[0]
    ramble.repository.global_namespace = _old[1]
    ramble.language.language_base.namespaces = _old[2]


# Experiments
def _exprs():
    """Get the singleton RepoPath instance for Ramble.

    Create a RepoPath, add it to sys.meta_path, and return it.

    TODO: consider not making this a singleton.
    """
    filename = os.getcwd()  # gross way to work around file for interactive testing
    repo_dirs = [os.path.join(filename, "test_repo")]
    if not repo_dirs:
        raise ramble.repository.NoRepoConfiguredError(
            "Benchpark configuration contains no experiment repositories."
        )

    with override_ramble_hardcoded_globals():
        path = ramble.repository.RepoPath(
            *repo_dirs, object_type=ObjectTypes.experiments
        )
    sys.meta_path.append(path)
    return path


paths = {
    ObjectTypes.experiments: llnl.util.lang.Singleton(_exprs),
}

#####################################
#     END TYPE SPECIFIC FUNCTIONALITY
#####################################


def all_object_names(object_type=default_type):
    """Convenience wrapper around ``ramble.repository.all_object_names()``."""  # noqa: E501
    return paths[object_type].all_object_names()


def get(spec, object_type=default_type):
    """Convenience wrapper around ``ramble.repository.get()``."""
    return paths[object_type].get(spec)


def set_path(repo, object_type=default_type):
    """Set the path singleton to a specific value.

    Overwrite ``path`` and register it as an importer in
    ``sys.meta_path`` if it is a ``Repo`` or ``RepoPath``.
    """
    global paths
    paths[object_type] = repo

    # make the new repo_path an importer if needed
    append = isinstance(repo, (ramble.repository.Repo, ramble.repository.RepoPath))
    if append:
        sys.meta_path.append(repo)
    return append


@contextlib.contextmanager
def additional_repository(repository, object_type=default_type):
    """Adds temporarily a repository to the default one.

    Args:
        repository: repository to be added
    """
    paths[object_type].put_first(repository)
    yield
    paths[object_type].remove(repository)


@contextlib.contextmanager
def use_repositories(*paths_and_repos, object_type=default_type):
    """Use the repositories passed as arguments within the context manager.

    Args:
        *paths_and_repos: paths to the repositories to be used, or
            already constructed Repo objects

    Returns:
        Corresponding RepoPath object
    """
    global paths

    # Construct a temporary RepoPath object from
    temporary_repositories = ramble.repository.RepoPath(
        *paths_and_repos, object_type=object_type
    )

    # Swap the current repository out
    saved = paths[object_type]
    remove_from_meta = set_path(temporary_repositories, object_type=object_type)

    yield temporary_repositories

    # Restore _path and sys.meta_path
    if remove_from_meta:
        sys.meta_path.remove(temporary_repositories)
    paths[object_type] = saved


def autospec(function):
    """Decorator that automatically converts the first argument of a
    function to a Spec.
    """

    @functools.wraps(function)
    def converter(self, spec_like, *args, **kwargs):
        if not isinstance(spec_like, benchpark.spec.ExperimentSpec):
            spec_like = benchpark.spec.ExperimentSpec(spec_like)
        return function(self, spec_like, *args, **kwargs)

    return converter


# Add the finder to sys.meta_path
REPOS_FINDER = ramble.repository.ReposFinder()
sys.meta_path.append(REPOS_FINDER)
