#!/usr/bin/env ramble-python

import ramble.workspace as ws

ws.workspace.workspace_config_path = ''

handles = []
for experiment in ["../../benchpark/experiments/saxpy/openmp/"]:
    w = ws.Workspace(experiment)
    handles.extend(w.config_sections['workspace']['raw_yaml']['ramble']['spack']['packages'].keys())


# print(handles)
# $ ./scratch.py
#   ['saxpy']
#
# The TODO here is to figure out how we want to iterate over all of the experiments
# (which really just means we find every directory under experiments that has a ramble.yaml in it).

#That will give us the list of handles that a system config will define

#We can then add arguments that let us specify which experiments we care about when setting up a system, so we don’t have to do all of them
