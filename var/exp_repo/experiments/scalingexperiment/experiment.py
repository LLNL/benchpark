from benchpark.directives import variant


class ScalingExperiment(object):
    variant(
        "scaling-factor",
        default="2",
        values=int,
        description="Factor by which to scale values of problem variables",
    )

    variant(
        "scaling-iterations",
        default="4",
        values=int,
        description="Number of experiments to be generated",
    )

    # input parameters:
    # 1. input_variables: dict[str, int | tuple(str), list[int]]. Input variables
    # For the first value in input_variables, if the value is a list, select the
    # index of its smallest element, 0 otherwise
    # Beginning with this index, generate a list of indexes of length equal to
    # the number of dimensions in an (ascending) round-robin order
    #
    # output:
    # scaling_order: list[int]. list of num_exprs values, one for each dimension,
    # starting with the minimum value of the first element in input_variables arranged
    # in an ascending round-robin order
    def configure_scaling_policy(self, input_variables):
        # compute the number of dimensions
        n_dims = 1
        for param in input_variables.values():
            if isinstance(param, list):
                n_dims = len(param)
                break

        # starting with the minimum value dim of the ordering parameter
        # compute the remaining n_dims-1 values in a round-robin manner
        val = input_variables[next(iter(input_variables))]
        min_dim = val.index(min(val)) if isinstance(val, list) else 0

        return [(min_dim + i) % n_dims for i in range(n_dims)]

    # input parameters:
    # 1. input_variables: dict[str, int | tuple(str), list[int]]. Dictionary of all variables
    # that need to be scaled. All variables are ordered as per the ordering policy of
    # the first element in input_variables. By default, this policy is to scale the
    # values beginning with the smallest dimension and proceeding in a RR manner through
    # the other dimensions
    #
    # 2. scaling_factor: int. Factor by which to scale the variables. All entries in
    # input_variables are scaled by the same factor
    #
    # 3. num_exprs: int. Number of experiments to be generated
    #
    # output:
    # output_variables: dict[str, int | list[int]]. num_exprs values for each
    # dimension of the input variable scaled by the scaling_factor according to the
    # scaling policy
    def scale_experiment_variables(self, input_variables, scaling_factor, num_exprs):
        # check if variable list is not empty
        if not input_variables:
            return {}

        # check if:
        # 1. input_variables key value pairs are either of type str: int or tuple(str): list(int)
        # 2. the length of key: tuple(str) is equal to length of value: list(int)
        # 3. all values of type list(int) have the same length i.e. the same number of dimensions
        n_dims = None
        for k, v in input_variables.items():
            if isinstance(k, str):
                if not isinstance(v, int):
                    raise RuntimeError("Invalid key-value pair. Expected type str->int")
            elif isinstance(k, tuple) and all(isinstance(s, str) for s in k):
                if isinstance(v, list) and all(isinstance(i, int) for i in v):
                    if len(k) != len(v):
                        raise RuntimeError(
                            "Invalid value. Length of key {k} does not match the length of value {v}"
                        )
                    else:
                        if not n_dims:
                            n_dims = len(v)
                        if len(v) != n_dims:
                            raise RuntimeError(
                                "Variables to be scaled have different dimensions"
                            )
                else:
                    raise RuntimeError(
                        "Invalid key-value pair. Expected type tuple(str)->list[int]"
                    )
            else:
                raise RuntimeError("Invalid key. Expected type str or tuple(str)")

        # compute the scaling order based on the ordering_param
        scaling_order_index = self.configure_scaling_policy(input_variables)

        scaled_variables = {}
        for key, val in input_variables.items():
            scaled_variables[key] = (
                [[v] for v in val] if isinstance(val, list) else [[val]]
            )

        for exp_num in range(num_exprs - 1):
            for param in scaled_variables.values():
                if len(param) == 1:
                    param[0].append(param[0][-1] * scaling_factor)
                else:
                    for p_idx, p_val in enumerate(param):
                        p_val.append(
                            p_val[-1] * scaling_factor
                            if p_idx
                            == scaling_order_index[exp_num % len(scaling_order_index)]
                            else p_val[-1]
                        )

        output_variables = {}
        for k, v in scaled_variables.items():
            if isinstance(k, tuple):
                for i in range(len(k)):
                    output_variables[k[i]] = v[i] if len(v[i]) > 1 else v[i][0]
            else:
                output_variables[k] = v[0] if len(v[0]) > 1 else v[0][0]
        return output_variables

