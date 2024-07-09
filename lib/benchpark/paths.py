# SPDX-License-Identifier: Apache-2.0

import os
import pathlib

benchpark_home = pathlib.Path(os.path.expanduser("~/.benchpark"))
global_ramble_path = benchpark_home / "ramble"
global_spack_path = benchpark_home / "spack"
