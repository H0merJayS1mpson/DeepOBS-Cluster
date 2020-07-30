#!/bin/bash
import numpy as np
import torch
import itertools
import inspect
import importlib.util
import os
import deepobs.abstract_runner.abstract_runner as daa
import sbatcher as sb
from subprocess import Popen, PIPE
import subprocess


class SlurmobsRunner():
    TESTPROBLEM = None
    OPTIMIZER = None
    OPTIMIZER_PATH = torch.optim
    OPTIMIZER_MODULE = None
    HYPERPARAMS_SPECS = {}
    HYPERPARAMS_VALUES = {}
    ADDITIONAL_PARAMS = {}
    SBATCH_PARAMS = {}
    sbatch_params_names = ["sbatch_job_name", "sbatch_nnodes", "sbatch_ntasks", "sbatch_cpus_per_task",
                           "sbatch_mem_per_cpu", "sbatch_gres", "sbatch_partition", "sbatch_time", "output"]
    d = {}
    dicts = []
    job_ids = []
    job_dict = {}

    def pathfinder(self, filename, directory="./"):
        command = "find"
        directory = directory
        flag = "-iname"
        fn = filename
        args = [command, directory, flag, fn]
        process = subprocess.run(args, stdout=subprocess.PIPE)
        path = process.stdout.decode().strip("\n")
        head, sep, tail = path.partition('\n')
        return head
        

    def __init__(self, d: dict):
        self.d = d
        

    def generate_configurations(self):
        self.TESTPROBLEM = self.d.pop('Testproblem')
        # MODULE IMPORT UND INSTANZ DER OPTIMIZER KLASSE GENERIEREN:
        # WENN PFAD SPEZIFIZIERT, PROBLEMATISCH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:
        if 'Optimizer Path' in self.d:
            spec = importlib.util.spec_from_file_location(self.d['Optimizer Module'], self.d['Optimizer Path'])
            optimizer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(optimizer_module)
            optimizer_class = getattr(optimizer_module, self.d.get('Optimizer'))
            self.OPTIMIZER = self.d.pop('Optimizer')
            self.OPTIMIZER_PATH = self.d.pop('Optimizer Path')
            self.OPTIMIZER_MODULE = self.d.pop('Optimizer Module')
        # WENN PYTORCH OPTIMIZER VERWENDET WIRD; ALSO KEIN(!!!!) PFAD FÜR IMOPRT SPEZIFIZIERT WURDE
        else:
            self.OPTIMIZER = self.d.pop('Optimizer')
            optimizer_class = getattr(self.OPTIMIZER_PATH, self.OPTIMIZER)

        # HYPERPARAMTER, ADDITIONAL PARAMETER, SBATCH PARAMETER VON SONSTIGEN TRENNEN:
        optimizer_sig = inspect.getfullargspec(optimizer_class)
        optimizer_sig = inspect.getfullargspec(optimizer_class).args
        runner_sig = inspect.getfullargspec(daa.Runner.run).args

        for param in optimizer_sig:
            if self.d.__contains__(param):
                self.HYPERPARAMS_VALUES[param] = self.d.get(param)
                self.d.pop(param)

        for param in runner_sig:
            if self.d.__contains__(param):
                self.ADDITIONAL_PARAMS[param] = self.d.get(param)
                self.d.pop(param)

        for param in self.sbatch_params_names:
            if self.d.__contains__(param):
                self.SBATCH_PARAMS[param] = self.d.get(param)
                self.d.pop(param)

        # dicts GENERIEREN, ENTHALTEN DIE PARAMTER WERTE FÜR DIE EINZELNEN TRAININGSDURCHLÄUFE:
        # FALLS TUPLE TYPE ==> INTERPRETIERE ALS RANGE (start, stop, inc)
        for key in self.HYPERPARAMS_VALUES:
            val = self.HYPERPARAMS_VALUES.get(key)
            if type(val) is tuple:
                self.HYPERPARAMS_VALUES.__setitem__(key, np.arange(*val))


        def single_to_set(dic):
            for key in dic:
                val = dic.get(key)
                if isinstance(val, np.ndarray):
                    dic.__setitem__(key, val.tolist())
                elif isinstance(val, list) or isinstance(val, set):
                    pass
                elif isinstance(val, str):
                    res = val.strip('][').split(', ')
                    for i, item in enumerate(res):
                        try:
                            x = float(item)
                            res[i] = x
                        except:
                            res[i] = item
                    dic.__setitem__(key, res)
                else:
                    dic.__setitem__(key, [val])

        single_to_set(self.HYPERPARAMS_VALUES)


        def product_dict(dictionary):
            keys = dictionary.keys()
            vals = dictionary.values()
            for instance in itertools.product(*vals):
                yield dict(zip(keys, instance))

        # ENTHÄLT DANN ALLE HYPERPARAMETER KOMBINATIONEN
        for item in (list(product_dict(
                self.HYPERPARAMS_VALUES))):  # FALLS ZUSÄTZLICHE PARAMETER EINBEZOGEN WERDEN SOLLEN: , **ADDITIONAL_PARAMS
            self.dicts.append(item)


        for key in self.dicts[0]:
            self.HYPERPARAMS_SPECS[key] = {'type': (type(self.dicts[0].__getitem__(key))).__name__}

    def run_batch_files(self):
        slurmrunnerpath = self.pathfinder('slurm_runner.py')
        i = 0
        if "output" in self.SBATCH_PARAMS:
            self.SBATCH_PARAMS["output"] = os.getcwd() + "/" + self.SBATCH_PARAMS["output"]
        for combination in self.dicts:
            with open('config' + str(i) + '.txt', 'w') as cf:
                cf.write(self.TESTPROBLEM + "\n")
                cf.write(self.OPTIMIZER + "\n")
                cf.write(str(self.HYPERPARAMS_SPECS) + "\n")
                cf.write(str(combination) + "\n")
                cf.write(str(self.ADDITIONAL_PARAMS) + "\n")
                if self.OPTIMIZER_MODULE is not None:
                    cf.write(self.OPTIMIZER_MODULE + "\n")
                if self.OPTIMIZER_PATH is not torch.optim:
                    cf.write(self.OPTIMIZER_PATH + "\n")
                cf.close()
            sbatchfile = sb.sBatcher(os.getcwd() + '/config' + str(i) + '.txt', self.SBATCH_PARAMS, slurmrunnerpath)
            sbatchfile.run_configurations(i)
            command = str(sbatchfile.FILE_DIRECTORY + '/' + sbatchfile.sbatch_params['sbatch_job_name'] + "_" + str(
                i) + ".sbatch")
            stdout = Popen('sbatch ' + command, shell=True, stdout=PIPE).stdout
            output = stdout.read()
            self.job_ids.append("".join(filter(str.isdigit, output.decode("utf-8"))))
            self.job_dict[self.job_ids[i]] = combination
            i += 1

        with open('job_dict.txt', 'w') as jd:
            jd.write(str(self.job_dict))

        removerpath = self.pathfinder("file_remover.py")
        batchpath = self.pathfinder("clean_up.sbatch")

        remover = sb.cleaner(removerpath, self.SBATCH_PARAMS['sbatch_job_name'],
                             os.getcwd() + "/job_dict.txt")
        remover.clean_up()
        os.system('sbatch --dependency=afterany:' + ','.join(self.job_ids) + ' ' + batchpath)

