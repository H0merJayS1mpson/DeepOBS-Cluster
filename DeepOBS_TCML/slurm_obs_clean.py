#!/bin/bash
import sys
from ast import literal_eval
from slurmobs_runner import SlurmobsRunner as sr

d = {}

with open(sys.argv[1], 'r') as f:
    # HYPERPARAMS_SPECS = dict(x.rstrip().split(None, 1) for x in f)
    for line in f:
        line = line.rstrip('\n')
        if ': ' in line:
            (key, val) = line.split(': ', 1)
            key = key.lower()
        elif ':' in line:
            raise SyntaxError('Missing whitespace folling colon at ' + str(line))
        try:
            d[key] = literal_eval(val)
        except Exception:
            d[key] = val

slurmy = sr(d)
slurmy.generate_configurations()
slurmy.run_batch_files()
