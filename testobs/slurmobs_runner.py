#!/bin/bash
import numpy as np
import itertools
import inspect
import importlib.util
import os
import sbatcher as sb
from subprocess import Popen, PIPE
import subprocess
import fnmatch
import copy


class SlurmobsRunner():
    TESTPROBLEM = None
    OPTIMIZER = None
    OPTIMIZER_PATH = 'torch.optim'
    OPTIMIZER_MODULE = None
    HYPERPARAMS_VALUES = {}
    ADDITIONAL_PARAMS = {}
    LR_EPOCHS = []
    LR_FACTORS = []
    SBATCH_PARAMS = {}
    INITIALIZATIONS = {}
    sbatch_params_names = ["sbatch_job_name", "sbatch_nnodes", "sbatch_ntasks", "sbatch_cpus_per_task",
                           "sbatch_mem_per_cpu", "sbatch_gres", "sbatch_partition", "sbatch_time", "output"]
    d = {}
    dicts = []
    additional_dicts = []
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

    def find_files(self, pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(int(name.lstrip('config').rstrip('.txt')))
        return result

    def single_to_set(self, dic):
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

    def __init__(self, d: dict):
        self.d = d

        # Hyperparameter case unabhängig machen
        if 'hyperparameters' in d:
            (d['hyperparameters']) = {k.lower(): v for k, v in (d['hyperparameters']).items()}
            # dicts GENERIEREN, ENTHALTEN DIE PARAMTER WERTE FÜR DIE EINZELNEN TRAININGSDURCHLÄUFE:
            # FALLS TUPLE TYPE ==> INTERPRETIERE ALS RANGE (start, stop, inc)
            for key in (d['hyperparameters']):
                val = (d['hyperparameters'])[key]
                if type(val) is tuple:
                    (d['hyperparameters']).__setitem__(key, np.arange(*val))


    def generate_configurations(self):
        # Werte in Felder speicherm
        self.TESTPROBLEM = self.d.pop('testproblem')
        self.OPTIMIZER = self.d.pop('optimizer')
        if 'optimizer path' in self.d:
            self.OPTIMIZER_PATH = self.d.pop('optimizer path')
            if 'optimizer module' in self.d:
                self.OPTIMIZER_MODULE = self.d.pop('optimizer module')
            else:
                print("error optimizer path was specified but not optimizer module")
                breakpoint()
        if 'hyperparameters' in self.d:
            self.HYPERPARAMS_VALUES = self.d.pop('hyperparameters')

        # Sbatch Parameter von sonstigen trennen:
        for param in self.sbatch_params_names:
            if param in self.d:
                self.SBATCH_PARAMS[param] = self.d.get(param)
                self.d.pop(param)

        # Formatierung der Hyperparameter Eingaben x -> [x] etc.
        self.single_to_set(self.HYPERPARAMS_VALUES)

        # single_to_set(self.ADDITIONAL_PARAMS)# FALLS ZUSÄTZLICHE PARAMETER EINBEZOGEN WERDEN SOLLEN: , **ADDITIONAL_PARAMS

        def product_dict(dictionary):
            keys = dictionary.keys()
            vals = dictionary.values()
            for instance in itertools.product(*vals):
                yield dict(zip(keys, instance))

        # ENTHÄLT DANN ALLE HYPERPARAMETER KOMBINATIONEN
        for item in (list(product_dict(
                self.HYPERPARAMS_VALUES))):
            self.dicts.append(item)

        if 'initializations' in self.d:
            self.INITIALIZATIONS = self.d.pop('initializations')

        if 'lr_sched_epochs' in self.d:
            self.LR_EPOCHS = self.d.pop('lr_sched_epochs')

        if 'lr_sched_factors' in self.d:
            self.LR_FACTORS = self.d.pop('lr_sched_factors')

        self.ADDITIONAL_PARAMS = self.d

        if self.ADDITIONAL_PARAMS:
            for key in (self.ADDITIONAL_PARAMS):
                val = (self.ADDITIONAL_PARAMS)[key]
                if type(val) is tuple:
                    (self.ADDITIONAL_PARAMS).__setitem__(key, np.arange(*val))

        # ENTHÄLT DANN ALLE ADDITIONAL_PARAMS KOMBINATIONEN
        self.single_to_set(self.ADDITIONAL_PARAMS)
        for item in (list(product_dict(
                self.ADDITIONAL_PARAMS))):
            if self.INITIALIZATIONS:
                item.update({'initializations': self.INITIALIZATIONS})
            self.additional_dicts.append(item)



    def run_batch_files(self):
        #interim = copy.deepcopy(self.ADDITIONAL_PARAMS)
        #interim.pop('initializations')
        #self.single_to_set(interim)
        slurmrunnerpath = self.pathfinder('slurm_runner.py')
        unavailable = self.find_files('config*.txt', os.getcwd())
        lower, upper = 0, 0
        i = 0
        if unavailable != []:
            lower = max(unavailable) + 1
        else:
            pass
        if "output" in self.SBATCH_PARAMS:
            self.SBATCH_PARAMS["output"] = os.getcwd() + "/" + self.SBATCH_PARAMS["output"]
        for combination in self.dicts:
            for dicts in self.additional_dicts:
                with open('config' + str(lower + i) + '.txt', 'w') as cf:
                    cf.write(self.TESTPROBLEM + "\n")
                    cf.write(self.OPTIMIZER + "\n")
                    cf.write(str(combination) + "\n")
                    if self.LR_EPOCHS and self.LR_FACTORS:
                        dicts.update({'lr_sched_epochs': self.LR_EPOCHS, 'lr_sched_factors': self.LR_FACTORS})
                    cf.write(str(dicts) + "\n")
                    if self.OPTIMIZER_MODULE:
                        cf.write(self.OPTIMIZER_MODULE + "\n")
                    if self.OPTIMIZER_PATH is not 'torch.optim':
                        cf.write(self.OPTIMIZER_PATH + "\n")
                    cf.close()
                sbatchfile = sb.sBatcher(os.getcwd() + '/config' + str(lower + i) + '.txt', self.SBATCH_PARAMS,
                                         slurmrunnerpath)
                sbatchfile.run_configurations(lower + i)
                command = str(sbatchfile.FILE_DIRECTORY + '/' + sbatchfile.sbatch_params['sbatch_job_name'] + "_" + str(
                    lower + i) + ".sbatch")
                stdout = Popen('sbatch ' + command, shell=True, stdout=PIPE).stdout
                output = stdout.read()
                self.job_ids.append("".join(filter(str.isdigit, output.decode("utf-8"))))
                #combination.update({'testproblem': self.TESTPROBLEM, 'optimizer': self.OPTIMIZER, "additional parameters": self.ADDITIONAL_PARAMS})
                self.job_dict[self.job_ids[i]] = combination.copy()
                self.job_dict[self.job_ids[i]].update({'testproblem': self.TESTPROBLEM, 'optimizer': self.OPTIMIZER, "additional parameters": dicts})
                i += 1

        upper = lower + i - 1
        with open('job_dict' + str(upper) + '.txt', 'w') as jd:
            jd.write(str(self.job_dict))

        removerpath = self.pathfinder("file_remover.py")

        if lower == 0:
            remover = sb.cleaner(removerpath, self.SBATCH_PARAMS['sbatch_job_name'],
                                 os.getcwd() + '/job_dict' + str(upper) + '.txt', lower, upper)

        else:
            remover = sb.cleaner(removerpath, self.SBATCH_PARAMS['sbatch_job_name'],
                                 os.getcwd() + '/job_dict' + str(upper) + '.txt', lower, upper)

        batchpath = remover.clean_up()
        os.system('sbatch --dependency=afterany:' + ','.join(self.job_ids) + ' ' + batchpath)
