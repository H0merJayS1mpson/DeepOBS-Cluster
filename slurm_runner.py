from deepobs import pytorch as pt
import sys
from ast import literal_eval
import importlib.util
import torch
import collections

d1 = ["TESTPROBLEM",
"OPTIMIZER",
"HYPERPARAMS_SPECS",
"HYPERPARAMS_VALUES",
"ADDITIONAL_PARAMS",
"OPTIMIZER_MODULE",
"OPTIMIZER_PATH"
]

l=[]

with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        l.append(line)

d = dict(zip(d1,l))

for key in d:
    if key == "ADDITIONAL_PARAMS" or key == 'HYPERPARAMS_VALUES' or key == "HYPERPARAMS_SPECS":
        try:
            d.__setitem__(key, eval(d[key]))
        except Exception:
            pass
        else:
            pass


del(sys.argv[1])

for key in d['HYPERPARAMS_SPECS']:
    d['HYPERPARAMS_SPECS'][key]['type'] = eval(d['HYPERPARAMS_SPECS'][key]['type'])


    # HYPERPARAMS_SPECS = dict(x.rstrip().split(None, 1) for x in f)
    # TESTPROBLEM = f.readline().rstrip('\n')
    # OPTIMIZER = f.readline().rstrip('\n')
    # HYPERPARAMS_SPECS = f.readline().rstrip('\n')
    # HYPERPARAMS_VALUES = literal_eval(f.readline().rstrip('\n'))
    # ADDITIONAL_PARAMS = literal_eval(f.readline().rstrip('\n'))


#MODULE IMPORT UND INSTANZ DER OPTIMIZER KLASSE GENERIEREN:
#WENN PFAD SPEZIFIZIERT, PROBLEMATISCH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:
if ("OPTIMIZER_PATH") in d:
    spec = importlib.util.spec_from_file_location(d['OPTIMIZER_MODULE'], d['OPTIMIZER_PATH'])
    optimizer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(optimizer_module)
    optimizer_class = getattr(optimizer_module, d.pop('OPTIMIZER')) #!!!!!!!!!!!!! ODER d.get(...) JE NACHDEM OB FEHLER AUFTRITT !!!!!!!!!!!!!
# WENN PYTORCH OPTIMIZER VERWENDET WIRD; ALSO KEIN(!!!!) PFAD FUER IMOPRT SPEZIFIZIERT WURDE
else:
    OPTIMIZER = d.pop('OPTIMIZER')
    optimizer_class = getattr(torch.optim, OPTIMIZER)


hyperparams = d.pop("HYPERPARAMS_SPECS")
runner = pt.runners.StandardRunner(optimizer_class, hyperparams)
runner.run(d.pop("TESTPROBLEM"), d.pop("HYPERPARAMS_VALUES"), **d.pop("ADDITIONAL_PARAMS"))

# try:
#     OPTIMIZER = MODULE.optimfromconfigfile
# except ImportError:
#     spec = importlib.util.spec_from_file_location("module.name", "/path/to/file.py")
#     foo = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(foo)
#     foo.MyClass()
