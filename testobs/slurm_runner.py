from deepobs import pytorch as pt
import sys
from ast import literal_eval
import importlib.util
import torch
import collections
import inspect
import deepobs.abstract_runner.abstract_runner as daa


TESTPROBLEM = None
OPTIMIZER = None
OPTIMIZER_PATH = torch.optim
OPTIMIZER_MODULE = None
HYPERPARAMS_SPECS = {}
HYPERPARAMS_VALUES = {}
ADDITIONAL_PARAMS = {}
SBATCH_PARAMS = {}

d1 = ["testproblem",
"optimizer",
"hyperparams",
"additional params",
"optimizer module",
"optimizer path",
"initializations"
]

l=[]

with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        l.append(line)

d = dict(zip(d1,l))

for key in d:
    if key == "additional params" or key == 'hyperparams':
        try:
            d.__setitem__(key, eval(d[key]))
        except Exception:
            pass
        else:
            pass


del(sys.argv[1])


if 'optimizer path' in d:
    spec = importlib.util.spec_from_file_location(d['optimizer module'], d['optimizer path'])
    optimizer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(optimizer_module)
    optimizer_class = getattr(optimizer_module, d.get('optimizer'))
    OPTIMIZER = d.pop('optimizer')
    OPTIMIZER_PATH = d.pop('optimizer path')
    OPTIMIZER_MODULE = d.pop('optimizer module')
else:
    OPTIMIZER = d.pop('optimizer')
    optimizer_class = getattr(OPTIMIZER_PATH, OPTIMIZER)

# HYPERPARAMTER, ADDITIONAL PARAMETER, SBATCH PARAMETER VON SONSTIGEN TRENNEN:
optimizer_sig = inspect.getfullargspec(optimizer_class)
optimizer_sig = inspect.getfullargspec(optimizer_class).args
runner_sig = inspect.getfullargspec(daa.Runner.run).args


unsupported_params = []
for param in d['hyperparams']:
    print(param)
    if param in runner_sig:
        pass
    else:
        unsupported_params.append(param)

for param in unsupported_params:
    d['hyperparams'].pop(param)

hyperparams_specs = {}

for key in d["hyperparams"]:
    hyperparams_specs[key] = type(d['hyperparams'][key])


runner = pt.runners.CustomRunner(optimizer_class, hyperparams_specs)
# print("HIER IST DAS INPUT KEYWORD DICTIONARY:       ", d)
runner.run(testproblem=d.pop('testproblem'), hyperparams=d.pop('hyperparams'), **d['additional params'])
