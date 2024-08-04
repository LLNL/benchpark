import enum
import pathlib
import re
from typing import Iterable, Iterator, List, Match, Optional, Union

import benchpark.paths
import benchpark.repo
import benchpark.runtime

bootstrapper = benchpark.runtime.RuntimeResources(benchpark.paths.benchpark_home)
bootstrapper.bootstrap()

import llnl.util.lang

repo_path = benchpark.repo.paths[benchpark.repo.ObjectTypes.experiments]
sys_repo = benchpark.repo.paths[benchpark.repo.ObjectTypes.systems]


class VariantMap(llnl.util.lang.HashableMap):
    def __init__(self, init: "VariantMap" = None):
        super().__init__()
        if init:
            self.dict = init.dict.copy()

    def __setitem__(self, name: str, values: Union[str, Iterable]):
        if name in self.dict:
            raise Exception(f"Cannot specify variant {name} twice")
        if isinstance(values, str):
            values = (values,)
        else:
            values = tuple(*values)
        super().__setitem__(name, values)

    def intersects(self, other: "VariantMap") -> bool:
        if isinstance(other, ConcreteVariantMap):
            return other.intersects(self)

        # always possible to constrain since abstract variants are multi-value
        return True

    def satisfies(self, other: "VariantMap") -> bool:
        if isinstance(other, ConcreteVariantMap):
            self == other

        return all(
            name in self and set(self[name]) >= set(other[name]) for name in other
        )

    @staticmethod
    def stringify(name: str, values: tuple) -> str:
        if len(values) == 1:
            if values[0].lower() == "true":
                return f"+{name}"
            if values[0].lower() == "false":
                return f"~{name}"
        return f"{name}={','.join(values)}"

    def __str__(self):
        return " ".join(
            self.stringify(name, values) for name, values in self.dict.items()
        )


class ConcreteVariantMap(VariantMap):
    def __setitem__(self, name, values):
        raise TypeError(f"{self.__class__} is immutable.")

    def intersects(self, other: VariantMap) -> bool:
        return self.satisfies(other)


class Spec(object):
    def __init__(self, str_or_spec: Optional[Union[str, "Spec"]] = None):
        self._name = None
        self._namespace = None
        self._variants = VariantMap()

        if isinstance(str_or_spec, Spec):
            self._dup(str_or_spec)
        elif isinstance(str_or_spec, str):
            self._parse(str_or_spec)
        elif str_or_spec is not None:
            msg = f"{self.__class__} can only be instantiated from {self.__class__} or str, "
            msg += f"not from {type(str_or_spec)}."
            raise NotImplementedError(msg)

    # getter/setter for each attribute so that ConcreteSpec can be immutable
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, value: str):
        self._namespace = value

    @property
    def variants(self):
        return self._variants

    # This one is probably unnecessary, but here for completeness
    @variants.setter
    def variants(self, value: VariantMap):
        self._variants = value

    def __eq__(self, other: "Spec"):
        if other is None:
            return False

        return (
            self.name == other.name
            and (
                self.namespace is None
                or other.namespace is None
                or self.namespace == other.namespace
            )
            and self.variants == other.variants
        )

    def __str__(self):
        string = ""
        if self.namespace is not None:
            string += f"{self.namespace}."
        if self.name is not None:
            string += self.name

        variants = str(self.variants)
        if not string:
            return variants
        string += f" {variants}" if variants else ""
        return string

    def __repr__(self):
        return str(self)

    def _dup(self, other: "Spec"):
        # operate on underlying types so it can be called on ConcreteSpec
        self._name = other.name
        self._namespace = other.namespace
        self._variants = other.variants

    def _parse(self, string: str):
        specs = SpecParser(
            type(self), string
        ).all_specs()  # parse spec of appropriate type
        assert len(specs) == 1, f"{string} does not parse to one spec"

        self._dup(specs[0])

    def intersects(self, other: Union[str, "Spec"]) -> bool:
        if not isinstance(other, Spec):
            other = type(self)(other)  # keep type from subclass
        return (
            (self.name is None or other.name is None or self.name == other.name)
            and (
                self.namespace is None
                or other.namespace is None
                or self.namespace == other.namespace
            )
            and self.variants.intersects(other.variants)
        )

    def satisfies(self, other: Union[str, "Spec"]) -> bool:
        if not isinstance(other, Spec):
            other = type(self)(other)  # keep type from subclass
        return (
            (other.name is None or self.name == other.name)
            and (other.namespace is None or self.namespace == other.namespace)
            and self.variants.satisfies(other.variants)
        )

    def concretize(self):
        raise NotImplementedError("Spec.concretize must be implemented by subclass")

    @property
    def object_class(self):
        raise NotImplementedError(
            f"{type(self)} does not implement object_class property"
        )


class ExperimentSpec(Spec):
    @property
    def experiment_class(self):
        return repo_path.get_obj_class(self.name)

    @property
    def object_class(self):
        # shared getter so that multiple spec types can be concretized similarly
        return self.experiment_class

    def concretize(self):
        return ConcreteExperimentSpec(self)


def autospec(function):
    """Decorator that automatically converts the first argument of a
    function to a Spec.
    """

    @functools.wraps(function)
    def converter(self, spec_like, *args, **kwargs):
        if not isinstance(spec_like, ExperimentSpec):
            spec_like = ExperimentSpec(spec_like)
        return function(self, spec_like, *args, **kwargs)

    return converter


class ConcreteSpec(Spec):
    def __init__(self, str_or_spec: Union[str, Spec]):
        super().__init__(str_or_spec)
        self._concretize()

    def __hash__(self):
        return hash((self.name, self.namespace, self.variants))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        raise TypeError(f"{self.__class__} is immutable")

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, value: str):
        raise TypeError(f"{self.__class__} is immutable")

    @property
    def variants(self):
        return self._variants

    @variants.setter
    def variants(self, value: str):
        raise TypeError(f"{self.__class__} is immutable")

    def _concretize(self):
        if not self.name:
            raise AnonymousSpecError(f"Cannot concretize anonymous {type(self)} {self}")

        if not self.namespace:
            # TODO interface combination ##
            self._namespace = self.object_class.namespace

        # TODO interface combination ##
        for name, variant in self.object_class.variants.items():
            if name not in self.variants:
                self._variants[name] = variant.default

        for name, values in self.variants.items():
            if name not in self.object_class.variants:
                raise Exception(f"{name} is not a valid variant of {self.name}")

            variant = self.object_class.variants[name]
            variant.validate_values(self.variants[name])

        # Convert to immutable type
        self._variants = ConcreteVariantMap(self.variants)


class ConcreteExperimentSpec(ConcreteSpec, ExperimentSpec):
    @property
    def experiment(self) -> "benchpark.Experiment":
        return self.experiment_class(self)


class SystemSpec(Spec):
    @property
    def system_class(self):
        cls = sys_repo.get_obj_class(self.name)
        # TODO: this shouldn't be necessary, but .package_dir isn't working
        cls.resource_location = pathlib.Path(sys_repo.filename_for_object_name(self.name)).parent
        return cls

    @property
    def object_class(self):
        # shared getter so that multiple spec types can be concretized similarly
        return self.system_class

    def concretize(self):
        return ConcreteSystemSpec(self)


class ConcreteSystemSpec(ConcreteSpec, SystemSpec):
    @property
    def system(self) -> "benchpark.System":
        return self.system_class(self)


# PARSING STUFF BELOW HERE

#: Valid name for specs and variants. Here we are not using
#: the previous "w[\w.-]*" since that would match most
#: characters that can be part of a word in any language
IDENTIFIER = r"(?:[a-zA-Z_0-9][a-zA-Z_0-9\-]*)"
DOTTED_IDENTIFIER = rf"(?:{IDENTIFIER}(?:\.{IDENTIFIER})+)"
NAME = r"[a-zA-Z_0-9][a-zA-Z_0-9\-.]*"

#: These are legal values that *can* be parsed bare, without quotes on the command line.
VALUE = r"(?:[a-zA-Z_0-9\-+\*.,:=\~\/\\]+)"

#: Regex with groups to use for splitting (optionally propagated) key-value pairs
SPLIT_KVP = re.compile(rf"^({NAME})=(.*)$")


class TokenBase(enum.Enum):
    """Base class for an enum type with a regex value"""

    def __new__(cls, *args, **kwargs):
        # See
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, regex):
        self.regex = regex

    def __str__(self):
        return f"{self._name_}"


class TokenType(TokenBase):
    """Enumeration of the different token kinds in the spec grammar.

    Order of declaration is extremely important, since text containing specs is parsed with a
    single regex obtained by ``"|".join(...)`` of all the regex in the order of declaration.
    """

    # variants
    BOOL_VARIANT = rf"(?:[~+-]\s*{NAME})"
    KEY_VALUE_PAIR = rf"(?:{NAME}=(?:{VALUE}))"
    # Package name
    FULLY_QUALIFIED_PACKAGE_NAME = rf"(?:{DOTTED_IDENTIFIER})"
    UNQUALIFIED_PACKAGE_NAME = rf"(?:{IDENTIFIER})"
    # White spaces
    WS = r"(?:\s+)"


class ErrorTokenType(TokenBase):
    """Enum with regexes for error analysis"""

    # Unexpected character
    UNEXPECTED = r"(?:.[\s]*)"


class Token:
    """Represents tokens; generated from input by lexer and fed to parse()."""

    __slots__ = "kind", "value", "start", "end"

    def __init__(
        self,
        kind: TokenBase,
        value: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ):
        self.kind = kind
        self.value = value
        self.start = start
        self.end = end

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"({self.kind}, {self.value})"

    def __eq__(self, other):
        return (self.kind == other.kind) and (self.value == other.value)


#: List of all the regexes used to match spec parts, in order of precedence
TOKEN_REGEXES = [rf"(?P<{token}>{token.regex})" for token in TokenType]
#: List of all valid regexes followed by error analysis regexes
ERROR_HANDLING_REGEXES = TOKEN_REGEXES + [
    rf"(?P<{token}>{token.regex})" for token in ErrorTokenType
]
#: Regex to scan a valid text
ALL_TOKENS = re.compile("|".join(TOKEN_REGEXES))
#: Regex to analyze an invalid text
ANALYSIS_REGEX = re.compile("|".join(ERROR_HANDLING_REGEXES))


def tokenize(text: str) -> Iterable[Token]:
    """Return a token generator from the text passed as input.

    Raises:
        SpecTokenizationError: if we can't tokenize anymore, but didn't reach the
            end of the input text.
    """
    scanner = ALL_TOKENS.scanner(text)  # type: ignore[attr-defined]
    match: Optional[Match] = None
    for match in iter(scanner.match, None):
        # The following two assertions are to help mypy
        msg = "unexpected value encountered during parsing. Please submit a bug report "
        assert match is not None, msg
        assert match.lastgroup is not None, msg
        yield Token(
            TokenType.__members__[match.lastgroup],
            match.group(),
            match.start(),
            match.end(),
        )

    if match is None and not text:
        # We just got an empty string
        return

    if match is None or match.end() != len(text):
        error_scanner = ANALYSIS_REGEX.scanner(text)
        matches = [m for m in iter(error_scanner.match, None)]
        raise SpecTokenizationError(matches, text)


class TokenContext:
    """Token context passed around by parsers"""

    __slots__ = "token_stream", "current_token", "next_token"

    def __init__(self, token_stream: Iterator[Token]):
        self.token_stream = token_stream
        self.current_token = None
        self.next_token = None
        self.advance()

    def advance(self):
        """Advance one token"""
        self.current_token, self.next_token = self.next_token, next(
            self.token_stream, None
        )

    def accept(self, kind: TokenType):
        """If the next token is of the specified kind, advance the stream and return True.
        Otherwise return False.
        """
        if self.next_token and self.next_token.kind == kind:
            self.advance()
            return True
        return False

    def expect(self, *kinds: TokenType):
        return self.next_token and self.next_token.kind in kinds


class SpecParser(object):
    __slots__ = "literal_str", "ctx", "type"

    def __init__(self, type, literal_str: str):
        self.literal_str = literal_str
        self.ctx = TokenContext(
            filter(lambda x: x.kind != TokenType.WS, tokenize(literal_str))
        )
        self.type = type

    def tokens(self) -> List[Token]:
        """Return the entire list of token from the initial text. White spaces are
        filtered out.
        """
        return list(
            filter(lambda x: x.kind != TokenType.WS, tokenize(self.literal_str))
        )

    def next_spec(self) -> Optional[Spec]:
        """Return the next spec parsed from text.

        Args:
            initial_spec: object where to parse the spec. If None a new one
                will be created.

        Return
            The spec that was parsed
        """
        if not self.ctx.next_token:
            return None

        spec = self.type()

        if self.ctx.accept(TokenType.UNQUALIFIED_PACKAGE_NAME):
            spec.name = self.ctx.current_token.value
        elif self.ctx.accept(TokenType.FULLY_QUALIFIED_PACKAGE_NAME):
            parts = self.ctx.current_token.value.split(".")
            name = parts[-1]
            namespace = ".".join(parts[:-1])
            spec.name = name
            spec.namespace = namespace

        while True:
            if self.ctx.accept(TokenType.BOOL_VARIANT):
                name = self.ctx.current_token.value[1:].strip()
                value = self.ctx.current_token.value[0] == "+"
                spec.variants[name] = str(value).lower()
            elif self.ctx.accept(TokenType.KEY_VALUE_PAIR):
                match = SPLIT_KVP.match(self.ctx.current_token.value)
                assert (
                    match
                ), f"SPLIT_KVP cannot split pair {self.ctx.current_token.value}"

                name, value = match.groups()
                spec.variants[name] = value
            else:
                break

        return spec

    def all_specs(self) -> List[Spec]:
        return list(iter(self.next_spec, None))


# ERROR HANDLING BELOW HERE


class AnonymousSpecError(Exception):
    pass


class SpecTokenizationError(Exception):
    """Syntax error in a spec string"""

    def __init__(self, matches, text):
        message = "unexpected tokens in the spec string\n"
        message += f"{text}"

        underline = "\n"
        for match in matches:
            if match.lastgroup == str(ErrorTokenType.UNEXPECTED):
                underline += f"{'^' * (match.end() - match.start())}"
                continue
            underline += f"{' ' * (match.end() - match.start())}"

        message += underline
        super().__init__(message)
