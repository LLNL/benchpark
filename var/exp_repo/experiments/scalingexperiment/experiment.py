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

    #def configure_scaling_policy(self, input_params: dict[str, int | list[int]], ordering_param:str):
    def configure_scaling_policy(self, input_params, ordering_param):
        # compute the number of dimensions
        n_dims = 1
        for param in input_params.values():
            if isinstance(param, list):
                n_dims = len(param)
                break

        # starting with the minimum value dim of the ordering parameter
        # compute the remaining n_dims-1 values in a round-robin manner
        val = input_params[ordering_param]
        min_dim = val.index(min(val)) if isinstance(val, list) else 0

        return [(min_dim + i) % n_dims for i in range(n_dims)]

    # input_params: dict[str, int | list[int]]. Dictionary of all variables that need to be scaled in same order
    # ordering_param: str. Name of the variable that decides the ordering. The default ordering is starting with the smallest dimension and proceeding in a RR manner
    # scaling_factor: int. Factor by which to scale the variables. All variables in input_params are scaled by the same factor
    # num_exprs: int. Number of experiments to be generated
    # scaled_params: dict[str, list[list[int]]]. num_exprs values for each dimension of the input variable scaled 
    # by the scaling_factor according to the scaling policy
    #def scale_experiment_variables(self, input_params: dict[str, int | list[int]], ordering_param:str=None, scaling_factor=2, num_exprs=4):
    def scale_experiment_variables(self, input_params, ordering_param=None, scaling_factor=2, num_exprs=4):
        # check if variable list is not empty
        if not input_params:
            return {}

        # if undefined, set ordering param to 
        # the first param in the input_params dict
        if not ordering_param:
            ordering_param = next(iter(input_params))

        # check if ordering_param is a valid key
        if not ordering_param in input_params:
            raise RuntimeError(
                "Invalid ordering paramater"
            )

        # check if:
        # 1. input_params has the type dict[str, int | list[int]] and 
        # 2. all the list variables have the same length i.e.
        # all multi-valued variables have the same dimension
        n_dims = None
        for k, v in input_params.items():
            if not isinstance(k, str):
                raise RuntimeError(
                    "Invalid key type. Must be a string."
                )
            if not (isinstance(v, int) or (isinstance(v, list) and all(isinstance(i, int) for i in v))):
                raise RuntimeError(
                    "Invalid value. Only int or list of int allowed."
                )
            if isinstance(v, list):
                if not n_dims:
                    n_dims = len(v)
                if len(v) != n_dims:
                    raise RuntimeError(
                        "Variables to be scaled have different dimensions"
                    )

        # compute the scaling order based on the ordering_param
        dim_scaling_order = self.configure_scaling_policy(input_params, ordering_param)

        scaled_params = {}
        for key, val in input_params.items():
            scaled_params[key] = [[v] for v in val] if isinstance(val, list) else [[val]] 

        for exp_num in range(num_exprs - 1):
            for param in scaled_params.values():
                if len(param) == 1:
                    param[0].append(param[0][-1]*scaling_factor)
                else:
                    for p_idx, p_val in enumerate(param):
                        p_val.append(p_val[-1]*scaling_factor if p_idx == dim_scaling_order[exp_num%len(dim_scaling_order)] else p_val[-1])

        return scaled_params
