# Copyright 2022-2024 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import abc
import collections
import os
import sys
import traceback
import types
import functools
import contextlib
import re
import importlib
import importlib.machinery
import importlib.util
import inspect
import stat
import shutil
import errno
import benchpark.naming as nm

try:
    from collections.abc import Mapping  # novm
except ImportError:
    from collections import Mapping


from enum import Enum

import llnl.util.lang
import benchpark.experiment_spec

global_namespace = "benchpark"

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


# Experiments
def _exprs():
    """Get the singleton RepoPath instance for Ramble.

    Create a RepoPath, add it to sys.meta_path, and return it.

    TODO: consider not making this a singleton.
    """
    filename = os.getcwd()  # gross way to work around file for interactive testing
    repo_dirs = [os.path.join(filename, "test_repo")]
    print(repo_dirs)
    if not repo_dirs:
        raise NoRepoConfiguredError(
            "Benchpark configuration contains no experiment repositories."
        )

    print("BEFORE PATH")
    try:
        path = RepoPath(*repo_dirs, object_type=ObjectTypes.experiments)
    except BaseException as e:
        print("EXCEPTION", e)
    print("AFTER PATH")
    sys.meta_path.append(path)
    print("RETURNING", path)
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
    append = isinstance(repo, (Repo, RepoPath))
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
    temporary_repositories = RepoPath(*paths_and_repos, object_type=object_type)

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
        if not isinstance(spec_like, benchpark.experiment_spec.ExperimentSpec):
            spec_like = benchpark.experiment_spec.ExperimentSpec(spec_like)
        return function(self, spec_like, *args, **kwargs)

    return converter


class ObjectNamespace(types.ModuleType):
    """Allow lazy loading of modules."""

    def __init__(self, namespace):
        super(ObjectNamespace, self).__init__(namespace)
        self.__file__ = "(benchpark namespace)"
        self.__path__ = []
        self.__name__ = namespace
        self.__experiment__ = namespace
        self.__modules = {}

    def __getattr__(self, name):
        """Getattr lazily loads modules if they're not already loaded."""
        submodule = self.__experiment__ + "." + name
        setattr(self, name, __import__(submodule))
        return getattr(self, name)


class RepoPath(object):
    """A RepoPath is a list of repos that function as one.

    It functions exactly like a Repo, but it operates on the combined
    results of the Repos in its list instead of on a single object
    repository.

    Args:
        repos (list): list Repo objects or paths to put in this RepoPath
    """

    def __init__(self, *repos, object_type=default_type):
        self.repos = []
        self.by_namespace = nm.NamespaceTrie()
        self.object_abbrev = type_definitions[object_type]["abbrev"]

        self.base_namespace = f"{global_namespace}.{self.object_abbrev}"

        self._all_object_names = None

        # Add each repo to this path.
        for repo in repos:
            try:
                if isinstance(repo, str):
                    repo = Repo(repo, object_type=object_type)
                self.put_last(repo)
            except RepoError as e:
                pass
                # logger.warn(
                #     "Failed to initialize repository: '%s'." % repo,
                #     e.message,
                #     "To remove the bad repository, run this command:",
                #     "    ramble repo rm %s" % repo,
                # )

    def put_first(self, repo):
        """Add repo first in the search path."""
        if isinstance(repo, RepoPath):
            for r in reversed(repo.repos):
                self.put_first(r)
            return

        self.repos.insert(0, repo)
        self.by_namespace[repo.full_namespace] = repo

    def put_last(self, repo):
        """Add repo last in the search path."""
        if isinstance(repo, RepoPath):
            for r in repo.repos:
                self.put_last(r)
            return

        self.repos.append(repo)

        # don't mask any higher-precedence repos with same namespace
        if repo.full_namespace not in self.by_namespace:
            self.by_namespace[repo.full_namespace] = repo

    def remove(self, repo):
        """Remove a repo from the search path."""
        if repo in self.repos:
            self.repos.remove(repo)

    def get_full_namespace(self, namespace):
        """Returns the full namespace of a repository, given its relative one."""
        return f"{self.base_namespace}.{namespace}"

    def get_repo(self, namespace, default=NOT_PROVIDED):
        """Get a repository by namespace.

        Arguments:

            namespace:

                Look up this namespace in the RepoPath, and return it if found.

        Optional Arguments:

            default:

                If default is provided, return it when the namespace
                isn't found.  If not, raise an UnknownNamespaceError.
        """
        full_namespace = self.get_full_namespace(namespace)
        if full_namespace not in self.by_namespace:
            if default == NOT_PROVIDED:
                raise UnknownNamespaceError(namespace)
            return default
        return self.by_namespace[full_namespace]

    def first_repo(self):
        """Get the first repo in precedence order."""
        return self.repos[0] if self.repos else None

    def all_object_names(self):
        """Return all unique object names in all repositories."""
        if self._all_object_names is None:
            all_objs = set()
            for repo in self.repos:
                for name in repo.all_object_names():
                    all_objs.add(name)
            self._all_object_names = sorted(all_objs, key=lambda n: n.lower())
        return self._all_object_names

    def objects_with_tags(self, *tags):
        r = set()
        for repo in self.repos:
            r |= set(repo.objects_with_tags(*tags))
        return sorted(r)

    def all_objects(self):
        for name in self.all_object_names():
            yield self.get(name)

    def all_object_classes(self):
        for name in self.all_object_names():
            yield self.get_obj_class(name)

    def find_module(self, fullname, path=None):
        """Implements precedence for overlaid namespaces.

        Loop checks each namespace in self.repos for objects, and
        also handles loading empty containing namespaces.

        """
        # namespaces are added to repo, and object modules are leaves.
        namespace, dot, module_name = fullname.rpartition(".")

        # If it's a module in some repo, or if it is the repo's
        # namespace, let the repo handle it.
        for repo in self.repos:
            if namespace == repo.full_namespace:
                if repo.real_name(module_name):
                    return repo
            elif fullname == repo.full_namespace:
                return repo

        # No repo provides the namespace, but it is a valid prefix of
        # something in the RepoPath.
        if self.by_namespace.is_prefix(fullname):
            return self

        return None

    def load_module(self, fullname):
        """Handles loading container namespaces when necessary.

        See ``Repo`` for how actual object modules are loaded.
        """
        if fullname in sys.modules:
            return sys.modules[fullname]

        if not self.by_namespace.is_prefix(fullname):
            raise ImportError("No such benchpark repo: %s" % fullname)

        module = ObjectNamespace(fullname)
        module.__loader__ = self
        sys.modules[fullname] = module
        return module

    def last_mtime(self):
        """Time a object file in this repo was last updated."""
        return max(repo.last_mtime() for repo in self.repos)

    def repo_for_obj(self, spec):
        """Given a spec, get the repository for its object."""
        # We don't @_autospec this function b/c it's called very frequently
        # and we want to avoid parsing str's into Specs unnecessarily.
        # logger.debug(f"Getting repo for obj {spec}")
        namespace = None
        if isinstance(spec, benchpark.experiment_spec.ExperimentSpec):
            namespace = spec.namespace
            name = spec.name
        else:
            # handle strings directly for speed instead of @_autospec'ing
            namespace, _, name = spec.rpartition(".")

        # logger.debug(f" Name and namespace = {namespace} - {name}")
        # If the spec already has a namespace, then return the
        # corresponding repo if we know about it.
        if namespace:
            fullspace = self.get_full_namespace(namespace)
            if fullspace not in self.by_namespace:
                raise UnknownNamespaceError(spec.namespace)
            return self.by_namespace[fullspace]

        # If there's no namespace, search in the RepoPath.
        for repo in self.repos:
            if name in repo:
                # logger.debug("Found repo...")
                return repo

        # If the object isn't in any repo, return the one with
        # highest precedence.  This is for commands like `ramble edit`
        # that can operate on objects that don't exist yet.
        return self.first_repo()

    @autospec
    def get(self, spec):
        """Returns the object associated with the supplied spec."""
        return self.repo_for_obj(spec).get(spec)

    def get_obj_class(self, obj_name):
        """Find a class for the spec's object and return the class object."""  # noqa: E501
        return self.repo_for_obj(obj_name).get_obj_class(obj_name)

    @autospec
    def dump_provenance(self, spec, path):
        """Dump provenance information for a spec to a particular path.

        This dumps the object file and any associated patch files.
        Raises UnknownObjectError if not found.
        """
        return self.repo_for_obj(spec).dump_provenance(spec, path)

    def dirname_for_object_name(self, obj_name):
        return self.repo_for_obj(obj_name).dirname_for_object_name(obj_name)

    def filename_for_object_name(self, obj_name):
        return self.repo_for_obj(obj_name).filename_for_object_name(obj_name)

    def exists(self, obj_name):
        """Whether object with the give name exists in the path's repos.

        Note that virtual objects do not "exist".
        """
        return any(repo.exists(obj_name) for repo in self.repos)

    # TODO: DWJ - Maybe we don't need this? Are we going to have virtual
    #             objects
    # def is_virtual(self, obj_name, use_index=True):
    #     """True if the object with this name is virtual,
    #        False otherwise.
    #
    #     Set `use_index` False when calling from a code block that could
    #     be run during the computation of the provider index."""
    #     have_name = obj_name is not None
    #     if have_name and not isinstance(obj_name, str):
    #         raise ValueError(
    #             "is_virtual(): expected object name, got %s" %
    #             type(obj_name))
    #     if use_index:
    #         return have_name and app_name in self.provider_index
    #     else:
    #         return have_name and (not self.exists(app_name) or
    #                               self.get_app_class(app_name).virtual)

    def __contains__(self, obj_name):
        return self.exists(obj_name)


class Repo(object):
    """Class representing a object repository in the filesystem.

    Each object repository must have a top-level configuration file
    called `repo.yaml`.

    Currently, `repo.yaml` this must define:

    `namespace`:
        A Python namespace where the repository's objects should live.

    """

    def __init__(self, root, object_type=default_type):
        """Instantiate an object repository from a filesystem path.

        Args:
            root: the root directory of the repository
        """
        # Root directory, containing _repo.yaml and object dirs
        # Allow roots to be ramble-relative by starting with '$ramble'
        self.root = root  # TODO CANONICALIZE
        self.object_file_name = type_definitions[object_type]["file_name"]
        self.object_type = object_type
        self.object_abbrev = type_definitions[object_type]["abbrev"]
        self.base_namespace = f"{global_namespace}.{self.object_abbrev}"

        # check and raise BadRepoError on fail.
        def check(condition, msg):
            if not condition:
                raise BadRepoError(msg)

        # Validate repository layout.
        self.config_name = None
        self.config_file = None
        for config in type_definitions[object_type]["accepted_configs"]:
            config_file = os.path.join(self.root, config)
            if os.path.exists(config_file):
                self.config_name = config
                self.config_file = config_file
        check(
            os.path.isfile(self.config_file),
            "No %s found in '%s'" % (self.config_name, root),
        )

        # Read configuration and validate namespace
        config = self._read_config()
        check(
            "namespace" in config,
            "%s must define a namespace." % os.path.join(root, self.config_name),
        )

        self.namespace = config["namespace"]
        check(
            re.match(r"[a-zA-Z][a-zA-Z0-9_.]+", self.namespace),
            ("Invalid namespace '%s' in repo '%s'. " % (self.namespace, self.root))
            + "Namespaces must be valid python identifiers separated by '.'",
        )

        objects_dir = (
            config["subdirectory"]
            if "subdirectory" in config
            else type_definitions[object_type]["dir_name"]
        )

        self.objects_path = os.path.join(self.root, objects_dir)
        check(
            os.path.isdir(self.objects_path),
            "No directory '%s' found in '%s'" % (objects_dir, root),
        )

        # Set up 'full_namespace' to include the super-namespace
        self.full_namespace = f"{self.base_namespace}.{self.namespace}"

        # Keep name components around for checking prefixes.
        self._names = self.full_namespace.split(".")

        # These are internal cache variables.
        self._modules = {}
        self._classes = {}
        self._instances = {}

        # Maps that goes from object name to corresponding file stat
        self._fast_object_checker = None

        # Indexes for this repository, computed lazily
        self._repo_index = None

        # make sure the namespace for objects in this repo exists.
        self._create_namespace()

    def _create_namespace(self):
        """Create this repo's namespace module and insert it into sys.modules.

        Ensures that modules loaded via the repo have a home, and that
        we don't get runtime warnings from Python's module system.

        """
        parent = None
        for i in range(1, len(self._names) + 1):
            ns = ".".join(self._names[:i])

            if ns not in sys.modules:
                module = ObjectNamespace(ns)
                module.__loader__ = self
                sys.modules[ns] = module

                # TODO: DWJ - Do we need this?
                # Ensure the namespace is an attribute of its parent,
                # if it has not been set by something else already.
                #
                # This ensures that we can do things like:
                #    import ramble.app.builtin.mpich as mpich
                if parent:
                    modname = self._names[i - 1]
                    setattr(parent, modname, module)
            else:
                # no need to set up a module
                module = sys.modules[ns]

            # but keep track of the parent in this loop
            parent = module

    def real_name(self, import_name):
        """Allow users to import Ramble objects using Python identifiers.

        A python identifier might map to many different Ramble object
        names due to hyphen/underscore ambiguity.

        Easy example:
            num3proxy   -> 3proxy

        Ambiguous:
            foo_bar -> foo_bar, foo-bar

        More ambiguous:
            foo_bar_baz -> foo_bar_baz, foo-bar-baz, foo_bar-baz, foo-bar_baz
        """
        if import_name in self:
            return import_name

        options = nm.possible_ramble_module_names(import_name)
        options.remove(import_name)
        for name in options:
            if name in self:
                return name
        return None

    def is_prefix(self, fullname):
        """True if fullname is a prefix of this Repo's namespace."""
        parts = fullname.split(".")
        return self._names[: len(parts)] == parts

    def find_module(self, fullname, path=None):
        """Python find_module import hook.

        Returns this Repo if it can load the module; None if not.
        """
        if self.is_prefix(fullname):
            return self

        namespace, dot, module_name = fullname.rpartition(".")
        if namespace == self.full_namespace:
            if self.real_name(module_name):
                return self

        return None

    def load_module(self, fullname):
        """Python importer load hook.

        Tries to load the module; raises an ImportError if it can't.
        """
        if fullname in sys.modules:
            return sys.modules[fullname]

        namespace, dot, module_name = fullname.rpartition(".")

        if self.is_prefix(fullname):
            module = ObjectNamespace(fullname)

        elif namespace == self.full_namespace:
            real_name = self.real_name(module_name)
            if not real_name:
                raise ImportError("No module %s in %s" % (module_name, self))
            module = self._get_obj_module(real_name)

        else:
            raise ImportError("No module %s in %s" % (fullname, self))

        module.__loader__ = self
        sys.modules[fullname] = module
        if namespace != fullname:
            parent = sys.modules[namespace]
            if not hasattr(parent, module_name):
                setattr(parent, module_name, module)

        return module

    def _read_config(self):
        """Check for a YAML config file in this db's root directory."""
        # THIS IS A HUGE HACK
        return {"namespace": "builtin"}

    @autospec
    def get(self, spec):
        """Returns the object associated with the supplied spec."""
        # NOTE: we only check whether the object is None here, not whether
        # it actually exists, because we have to load it anyway, and that ends
        # up checking for existence. We avoid constructing
        # FastObjectChecker, which will stat all objects.
        #        logger.debug(f"Getting obj {spec} from repo")
        if spec.name is None:
            raise UnknownObjectError(None, self)

        if spec.namespace and spec.namespace != self.namespace:
            raise UnknownObjectError(spec.name, self.namespace)

        object_class = self.get_obj_class(spec.name)
        try:
            return object_class(self.object_path(spec))
        except ramble.error.RambleError:
            # pass these through as their error messages will be fine.
            raise
        except Exception as e:
            #            logger.debug(e)

            # Make sure other errors in constructors hit the error
            # handler by wrapping them
            if ramble.config.get("config:debug"):
                sys.excepthook(*sys.exc_info())
            raise FailedConstructorError(spec.fullname, *sys.exc_info())

    @autospec
    def dump_provenance(self, spec, path):
        """Dump provenance information for a spec to a particular path.

        This dumps the object file.
        Raises UnknownObjectError if not found.
        """
        if spec.namespace and spec.namespace != self.namespace:
            raise UnknownObjectError(
                f"Repository {self.namespace} does not "
                f"contain {self.object_type.name} {spec.fullname}."
            )

        # Install the object's .py file itself.
        fs.install(self.filename_for_object_name(spec.name), path)

    def purge(self):
        """Clear entire object instance cache."""
        self._instances.clear()

    @property
    def index(self):
        """Construct the index for this repo lazily."""
        if self._repo_index is None:
            self._repo_index = RepoIndex(
                self._obj_checker, self.namespace, self.object_type
            )
            self._repo_index.add_indexer("tags", TagIndexer(self.object_type))
        return self._repo_index

    @property
    def tag_index(self):
        """Index of tags and which objects they're defined on."""
        return self.index["tags"]

    def dirname_for_object_name(self, obj_name):
        """Get the directory name for a particular object.  This is the
        directory that contains its object.py file."""
        return os.path.join(self.objects_path, obj_name)

    def filename_for_object_name(self, obj_name):
        """Get the filename for the module we should load for a particular
        object.  objects for a Repo live in
        ``$root/<object_name>/<object_type>.py``

        This will return a proper <object_type>.py path even if the
        object doesn't exist yet, so callers will need to ensure
        the object exists before importing.
        """
        obj_dir = self.dirname_for_object_name(obj_name)
        return os.path.join(obj_dir, self.object_file_name)

    @autospec
    def object_path(self, spec):
        return os.path.join(
            self.objects_path,
            self.dirname_for_object_name(spec.name),
            self.filename_for_object_name(spec.name),
        )

    def all_object_names(self):
        """Returns a sorted list of all object names in the Repo."""
        names = sorted(self._obj_checker.keys())
        return names

    def objects_with_tags(self, *tags):
        v = set(self.all_object_names())
        index = self.tag_index

        for t in tags:
            t = t.lower()
            v &= set(index[t])

        return sorted(v)

    def all_objects(self):
        """Iterator over all objects in the repository.

        Use this with care, because loading objects is slow.

        """
        for name in self.all_object_names():
            yield self.get(name)

    def all_object_classes(self):
        """Iterator over all object *classes* in the repository.

        Use this with care, because loading objects is slow.
        """
        for name in self.all_object_names():
            yield self.get_obj_class(name)

    def exists(self, obj_name):
        """Whether a object with the supplied name exists."""
        if obj_name is None:
            return False

        # if the FastObjectChecker is already constructed, use it
        if self._fast_object_checker:
            return obj_name in self._obj_checker

        # if not, check for the object.py file
        path = self.filename_for_object_name(obj_name)
        return os.path.exists(path)

    def last_mtime(self):
        """Time a object file in this repo was last updated."""
        return self._obj_checker.last_mtime()

    def _get_obj_module(self, obj_name):
        """Create a module for a particular object.

        This caches the module within this Repo *instance*.  It does
        *not* add it to ``sys.modules``.  So, you can construct
        multiple Repos for testing and ensure that the module will be
        loaded once per repo.

        """
        if obj_name not in self._modules:
            file_path = self.filename_for_object_name(obj_name)

            if not os.path.exists(file_path):
                raise UnknownObjectError(obj_name, self)

            if not os.path.isfile(file_path):
                raise Exception(f"Something's wrong. '{file_path}' is not a file!")

            if not os.access(file_path, os.R_OK):
                raise Exception(f"Cannot read '{file_path}'!")

            # e.g., ramble.app.builtin.mpich
            fullname = "%s.%s" % (self.full_namespace, obj_name)

            try:
                loader = importlib.machinery.SourceFileLoader(fullname, file_path)
                module = types.ModuleType(loader.name)
                loader.exec_module(module)
            except SyntaxError as e:
                # SyntaxError strips the path from the filename so we need to
                # manually construct the error message in order to give the
                # user the correct .py where the syntax error is
                # located
                raise SyntaxError(
                    "invalid syntax in {0:}, line {1:}".format(file_path, e.lineno)
                )

            module.__object__ = self.full_namespace
            module.__loader__ = self
            self._modules[obj_name] = module

        return self._modules[obj_name]

    def get_obj_class(self, obj_name):
        """Get the class for the object out of its module.

        First loads (or fetches from cache) a module for the
        object. Then extracts the object class from the module
        according to Ramble's naming convention.
        """
        namespace, _, obj_name = obj_name.rpartition(".")
        if namespace and (namespace != self.namespace):
            raise InvalidNamespaceError(
                "Invalid namespace for %s repo: %s" % (self.namespace, namespace)
            )

        class_name = nm.mod_to_class(obj_name)
        # logger.debug(f" Class name = {class_name}")
        module = self._get_obj_module(obj_name)

        cls = getattr(module, class_name)
        if not inspect.isclass(cls):
            raise Exception(f"{obj_name}.{class_name} is not a class")

        return cls

    def __str__(self):
        return "[Repo '%s' at '%s']" % (self.namespace, self.root)

    def __repr__(self):
        return self.__str__()

    def __contains__(self, obj_name):
        return self.exists(obj_name)


class RepositoryNamespace(types.ModuleType):
    """Allow lazy loading of modules."""

    def __init__(self, namespace):
        super(RepositoryNamespace, self).__init__(namespace)
        self.__file__ = "(repository namespace)"
        self.__path__ = []
        self.__name__ = namespace
        self.__package__ = namespace
        self.__modules = {}

    def __getattr__(self, name):
        """Getattr lazily loads modules if they're not already loaded."""
        submodule = self.__package__ + "." + name
        try:
            setattr(self, name, __import__(submodule))
        except ImportError:
            msg = "'{0}' object has no attribute {1}"
            raise AttributeError(msg.format(type(self), name))
        return getattr(self, name)


class RepoLoader(importlib.machinery.SourceFileLoader):
    """Loads a Python module associated with a object in specific repository"""

    #: Code in ``_object_prepend`` is prepended to imported objects.
    _object_prepend = "from __future__ import absolute_import;"

    def __init__(self, fullname, repo, object_name):
        self.repo = repo
        self.object_name = object_name
        self.object_py = repo.filename_for_object_name(object_name)
        self.fullname = fullname
        super(RepoLoader, self).__init__(
            self.fullname, self.object_py, prepend=self._object_prepend
        )


class RepositoryNamespaceLoader(object):
    def create_module(self, spec):
        return RepositoryNamespace(spec.name)

    def exec_module(self, module):
        module.__loader__ = self


class ReposFinder(object):
    """MetaPathFinder class that loads a Python module corresponding to an object

    Return a loader based on the inspection of the current global repository list.
    """

    def __init__(self, object_type=default_type):
        self.object_type = object_type

    def find_spec(self, fullname, python_path, target=None):
        # "target" is not None only when calling importlib.reload()
        if target is not None:
            raise RuntimeError('cannot reload module "{0}"'.format(fullname))

        # Preferred API from https://peps.python.org/pep-0451/
        if not fullname.startswith("benchpark."):
            return None

        loader = self.compute_loader(fullname)
        if loader is None:
            return None
        return importlib.util.spec_from_loader(fullname, loader)

    def compute_loader(self, fullname):
        # namespaces are added to repo, and object modules are leaves.
        namespace, dot, module_name = fullname.rpartition(".")

        # If it's a module in some repo, or if it is the repo's
        # namespace, let the repo handle it.
        for repo in paths[self.object_type].repos:
            # We are using the namespace of the repo and the repo contains the object
            if namespace == repo.full_namespace:
                # With 2 nested conditionals we can call "repo.real_name" only once
                object_name = repo.real_name(module_name)
                if object_name:
                    return RepoLoader(fullname, repo, object_name)

            # We are importing a full namespace like 'spack.pkg.builtin'
            if fullname == repo.full_namespace:
                return RepositoryNamespaceLoader()

        # No repo provides the namespace, but it is a valid prefix of
        # something in the RepoPath.
        if paths[self.object_type].by_namespace.is_prefix(fullname):
            return RepositoryNamespaceLoader()

        return None


# Add the finder to sys.meta_path
REPOS_FINDER = ReposFinder()
sys.meta_path.append(REPOS_FINDER)


class RepoError(benchpark.error.BenchparkError):
    """Superclass for repository-related errors."""


class NoRepoConfiguredError(RepoError):
    """Raised when there are no repositories configured."""


class InvalidNamespaceError(RepoError):
    """Raised when an invalid namespace is encountered."""


class BadRepoError(RepoError):
    """Raised when repo layout is invalid."""


class UnknownEntityError(RepoError):
    """Raised when we encounter a object ramble doesn't have."""


class IndexError(RepoError):
    """Raised when there's an error with an index."""


class UnknownObjectError(UnknownEntityError):
    """Raised when we encounter an object ramble doesn't have."""

    def __init__(self, name, repo=None, object_type="Object"):
        msg = None
        long_msg = None

        if name:
            if repo:
                msg = f"{object_type} '{name}' not found in repository '{repo.root}'"
            else:
                msg = f"{object_type} '{name}' not found."

            # Special handling for specs that may have been intended as
            # filenames: prompt the user to ask whether they intended to write
            # './<name>'.
            if name.endswith(".yaml"):
                long_msg = "Did you mean to specify a filename with './{0}'?"
                long_msg = long_msg.format(name)
        else:
            msg = f"Attempting to retrieve anonymous {object_type}."

        super(UnknownObjectError, self).__init__(msg, long_msg)
        self.name = name


class UnknownNamespaceError(UnknownEntityError):
    """Raised when we encounter an unknown namespace"""

    def __init__(self, namespace):
        super(UnknownNamespaceError, self).__init__("Unknown namespace: %s" % namespace)


class FailedConstructorError(RepoError):
    """Raised when an object's class constructor fails."""

    def __init__(self, name, exc_type, exc_obj, exc_tb, object_type=None):
        super(FailedConstructorError, self).__init__(
            f"Class constructor failed for {object_type} '%s'." % name,
            "\nCaused by:\n"
            + ("%s: %s\n" % (exc_type.__name__, exc_obj))
            + "".join(traceback.format_tb(exc_tb)),
        )
        self.name = name
