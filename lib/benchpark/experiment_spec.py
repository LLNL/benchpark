import enum
import re
from typing import Iterable, Iterator, List, Optional, Union
import llnl.util.lang
import benchpark.repo


class VariantMap(llnl.util.lang.HashableMap):
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
        " ".join(self.stringify(name, values) for name, values in self.dict.items())


class ConcreteVariantMap(VariantMap):
    def __setitem__(self, name, values):
        raise TypeError(f"{self.__class__} is immutable.")

    def intersects(self, other: VariantMap) -> bool:
        return self.satisfies(other)


class ExperimentSpec(object):
    def __init__(self, str_or_spec: Optional[Union[str, "ExperimentSpec"]] = None):
        self._name = None
        self._namespace = None
        self._variants = VariantMap()

        if isinstance(str_or_spec, ExperimentSpec):
            self._dup(str_or_spec)
        elif isinstance(str_or_spec, str):
            self._parse(str_or_spec)
        elif str_or_spec is not None:
            msg = f"{self.__class__} can only be instantiated from {self.__class__} or str, "
            msg += f"not from {type(str_or_spec)}."
            raise NotImplementedError(msg)

    ### getter/setter for each attribute so that ConcreteExperimentSpec can be immutable ###
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

    def __eq__(self, other: "ExperimentSpec"):
        return (
            self.name == other.name
            and (
                self.namespace is None
                or other.namespace is None
                or self.namespace == other.namespace
            )
            and self.variants == other.variants
        )

    def _dup(self, other: "ExperimentSpec"):
        # operate on underlying types so it can be called on ConcreteExperimentSpec
        self._name = other.name
        self._namespace = other.namespace
        self._variants = other.variants

    def _parse(self, string: str):
        specs = ExperimentSpecParser(string).all_specs()
        assert len(specs) == 1, f"{string} does not parse to one spec"

        self._dup(specs[0])

    def intersects(self, other: Union[str, "ExperimentSpec"]) -> bool:
        if not isinstance(other, ExperimentSpec):
            other = ExperimentSpec(other)
        return (
            (self.name is None or other.name is None or self.name == other.name)
            and (
                self.namespace is None
                or other.namespace is None
                or self.namespace == other.namespace
            )
            and self.variants.intersects(other.variants)
        )

    def satisfies(self, other: Union[str, "ExperimentSpec"]) -> bool:
        if not isinstance(other, ExperimentSpec):
            other = ExperimentSpec(other)
        return (
            (other.name is None or self.name == other.name)
            and (other.namespace is None or self.namespace == other.namespace)
            and self.variants.satisfies(other.variants)
        )

    def concretize(self):
        return ConcreteExperimentSpec(self)

    @property
    def experiment_class(self):
        ## TODO interface combination ##
        return benchpark.repo.get_experiment_class(self.name)


class ConcreteExperimentSpec(ExperimentSpec):
    def __init__(self, str_or_spec: Union[str, ExperimentSpec]):
        super().__init__(*args, **kwargs)
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
            raise AnonymousSpecError(
                f"Cannot concretize anonymous ExperimentSpec {self}"
            )

        if not self.namespace:
            ## TODO interface combination ##
            self._namespace = benchpark.repo.namespace_for_experiment(self.name)

        ## TODO interface combination ##
        for name, variant in self.experiment_class.variants.items():
            if name not in self.variants:
                self._variants[name] = variant.default
            else:
                # raise if the value is invalid
                ## TODO interface combination ##
                variant.validate(self.variants[name])

        # Convert to immutable type
        self._variants = ConcreteVariantMap(self.variants)

    @property
    def experiment(self) -> "benchpark.Experiment":
        return self.experiment_class(self)


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


class ExperimentSpecParser(object):
    __slots__ = "literal_str", "ctx"

    def __init__(self, literal_str: str):
        self.literal_str = literal_str
        self.ctx = TokenContext(
            filter(lambda x: x.kind != TokenType.WS, tokenize(literal_str))
        )

    def tokens(self) -> List[Token]:
        """Return the entire list of token from the initial text. White spaces are
        filtered out.
        """
        return list(
            filter(lambda x: x.kind != TokenType.WS, tokenize(self.literal_str))
        )

    def next_spec(self) -> Optional[ExperimentSpec]:
        """Return the next spec parsed from text.

        Args:
            initial_spec: object where to parse the spec. If None a new one
                will be created.

        Return
            The spec that was parsed
        """
        if not self.ctx.next_token:
            return None

        spec = ExperimentSpec()

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
                spec[name] = value
            else:
                break

        return spec

    def all_specs(self) -> List[ExperimentSpec]:
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

        message += color.colorize(f"@*r{{{underline}}}")
        super().__init__(message)
