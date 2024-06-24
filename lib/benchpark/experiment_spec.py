import llnl.util.lang
import benchpark.repo


class VariantMap(llnl.util.lang.HashableMap):
    def __setitem__(self, name, values):
        if name in self.dict:
            raise Exception(f"Cannot specify variant {name} twice")
        if isinstance(values, str):
            values = (values,)
        else:
            values = tuple(*values)
        super().__setitem__(name, values)

    def intersects(self, other):
        # TODO implement
        pass

    def satisfies(self, other):
        # TODO implement
        pass

    @staticmethod
    def stringify(name, values):
        if len(values) == 1:
            if values[0].lower() == "true":
                return f"+{name}"
            if values[0].lower() == "false":
                return f"~{name}"
        return f"{name}={','.join(values)}"

    def __str__(self):
        ' '.join(
            self.stringify(name, values)
            for name, values in self.dict.items()
        )


class ConcreteVariantMap(VariantMap):
    def __setitem__(self, name, variant_spec):
        raise TypeError(f"{self.__class__} is immutable.")

    def intersects(self, other):
        # TODO implement
        pass

    def satisfies(self, other):
        # TODO implement
        pass


class ExperimentSpec(ExperimentSpec):
    def __init__(self, str_or_spec):
        self._name = None
        self._namespace = None
        self._variants = VariantMap()

        if isinstance(str_or_spec, ExperimentSpec):
            self._dup(str_or_spec)
        elif isinstance(str_or_spec, str):
            self._parse(str_or_spec)
        else:
            msg = f"{self.__class__} can only be instantiated from {self.__class__} or str, "
            msg += f"not from {type(str_or_spec)}".
            raise NotImplementedError(msg)

    ### getter/setter for each attribute so that ConcreteExperimentSpec can be immutable ###
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, value):
        self._namespace = value

    @property
    def variants(self):
        return self._variants

    # This one is probably unnecessary, but here for completeness
    @variants.setter
    def variants(self, value):
        self._variants = value  # value is an entire dict

    def __eq__(self, other):
        return (
            self.name == other.name and
            (self.namespace is None or other.namespace is None or self.namespace == other.namespace) and
            self.variants == other.variants
        )

    def _dup(self, other):
        # operate on underlying types so it can be called on ConcreteExperimentSpec
        self._name = other.name
        self._namespace = other.namespace
        self._variants = other.variants

    def _parse(self, str):
        # TODO implement
        pass

    def intersects(self, other):
        # TODO implement
        pass

    def satisfies(self, other):
        # TODO implement
        pass

    def concretize(self):
        return ConcreteExperimentSpec(self)

    @property
    def experiment_class(self):
        ## TODO interface combination ##
        return benchpark.repo.get_experiment_class(self.name)


class ConcreteExperimentSpec(ExperimentSpec):
    def __init__(self, str_or_spec):
        super().__init__(*args, **kwargs)
        self._concretize()

    def __hash__(self):
        return hash((self.name, self.namespace, self.variants))

    @name.setter
    def name(self, value):
        raise TypeError(f"{self.__class__} is immutable")

    @namespace.setter
    def namespace(self, value)
        raise TypeError(f"{self.__class__} is immutable")

    @variants.setter
    def variants(self, value):
        raise TypeError(f"{self.__class__} is immutable")

    def _concretize(self):
        if not self.name:
            raise AnonymousSpecError(f"Cannot concretize anonymous ExperimentSpec {self}")

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

    def intersects(self, other):
        # TODO implement
        pass

    def satisfies(self, other):
        # TODO implement
        pass

    @property
    def experiment(self):
        return self.experiment_class(self)


class AnonymousSpecError(Exception):
    pass
