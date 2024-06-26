# TODO
from benchpark.experiment import Experiment
from benchpark.directives import *


class Saxpy(Experiment):
    variant(
        "programming_model",
        default="openmp",
        values=("openmp", "cuda", "rocm"),
        description="on-node parallelism model",
    )
