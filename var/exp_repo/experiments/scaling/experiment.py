from benchpark.directives import variant


class Scaling(object):
    variant(
        "strong-scaling-factor",
        default="2",
        description="Strong-scaling factor (factor by which to increase resources)",
    )

    variant(
        "strong-scaling-num-exprs",
        default="4",
        description="Number of strong-scaling experiments",
    )

    variant(
        "weak-scaling-factor",
        default="2",
        description="Weak-scaling factor (factor by which to increase resources and problem sizes)",
    )

    variant(
        "weak-scaling-num-exprs",
        default="4",
        description="Number of weak-scaling experiments",
    )

    def compute_round_robin_order(self, resource_list):   
        # start with the minimum dim in the list and compute-the round robin list
        min_dim = resource_list.index(min(resource_list))
        total_dims = len(resource_list)
        return [(min_dim + i) % total_dims for i in range(total_dims)]

    def generate_strong_scaling_parameters(self, initial_resource_list: list):
        scaling_factor = int(self.spec.variants["strong-scaling-factor"][0])
        num_exprs = int(self.spec.variants["strong-scaling-num-exprs"][0]) - 1
        round_robin_order = self.compute_round_robin_order(initial_resource_list)
        resource_list = [[x] for x in initial_resource_list]

        while num_exprs > 0:
            for idx in round_robin_order:
                for i, r in enumerate(resource_list):
                    r.append(r[-1]*scaling_factor if i == idx else r[-1])
                num_exprs=num_exprs-1
                if not num_exprs:
                    break
        return resource_list

    def generate_weak_scaling_parameters(self, initial_resource_list: list, initial_problem_size_list: list):
        scaling_factor = int(self.spec.variants["weak-scaling-factor"][0])
        num_exprs = int(self.spec.variants["weak-scaling-num-exprs"][0]) - 1
        round_robin_order = self.compute_round_robin_order(initial_resource_list)
        resource_list = [[x] for x in initial_resource_list]
        problem_size_list = [[x] for x in initial_problem_size_list]

        while num_exprs > 0:
            for idx in round_robin_order:
                for (i, r), p in zip(enumerate(resource_list), problem_size_list):
                    r.append(r[-1]*scaling_factor if i == idx else r[-1])
                    p.append(p[-1]*scaling_factor if i == idx else p[-1])
                num_exprs=num_exprs-1
                if not num_exprs:
                    break
        return resource_list,problem_size_list
