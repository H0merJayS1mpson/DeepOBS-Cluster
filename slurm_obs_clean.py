#!/bin/bash
import sys
from ast import literal_eval
import slurmobs_runner as sr

d = {}

with open(sys.argv[1], 'r') as f:
    # HYPERPARAMS_SPECS = dict(x.rstrip().split(None, 1) for x in f)
    for line in f:
        line = line.rstrip('\n')
        (key, val) = line.split(': ')
        try:
            d[key] = literal_eval(val)
        except Exception:
            d[key] = val

slurmy = sr.SlurmobsRunner(d)
slurmy.generate_configurations()
slurmy.run_batch_files()
