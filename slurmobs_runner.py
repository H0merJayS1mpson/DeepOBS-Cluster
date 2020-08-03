#!/bin/bash
import numpy as np
import itertools
import inspect
import importlib.util
import os
import sbatcher as sb
from subprocess import Popen, PIPE
import subprocess


class SlurmobsRunner():
    TESTPROBLEM = None
    OPTIMIZER = None
    OPTIMIZER_PATH = 'torch.optim'
    OPTIMIZER_MODULE = None
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

        # Hyperparameter cas unabhängig machen
        if 'hyperparameters' in d:
            (d['hyperparameters']) = {k.lower(): v for k, v in (d['hyperparameters']).items()}
            # dicts GENERIEREN, ENTHALTEN DIE PARAMTER WERTE FÜR DIE EINZELNEN TRAININGSDURCHLÄUFE:
            # FALLS TUPLE TYPE ==> INTERPRETIERE ALS RANGE (start, stop, inc)
            for key in (d['hyperparameters']):
                val = (d['hyperparameters'])[key]
                if type(val) is tuple:
                    (d['hyperparameters']).__setitem__(key, np.arange(*val))

    # with open(sys.argv[1], 'r') as f:
    #     # HYPERPARAMS_SPECS = dict(x.rstrip().split(None, 1) for x in f)
    #     for line in f:
    #         line = line.rstrip('\n')
    #         (key, val) = line.split(': ')
    #         try:
    #             d[key] = literal_eval(val)
    #         except Exception:
    #             d[key] = val

    def generate_configurations(self):
        # Werte in Felder speicherm
        self.TESTPROBLEM = self.d.pop('testproblem')
        self.OPTIMIZER = self.d.pop('optimizer')
        if self.d.__contains__('optimizer path'):
            self.OPTIMIZER_PATH =self.d.pop('optimizer path')
            if self.d.__contains__('optimizer module'):
                self.OPTIMIZER_MODULE = self.d.pop('optimizer module')
            else:
                print("error optimizer path was specified but not optimizer module")
                breakpoint()
        if 'hyperparameters' in self.d:
            self.HYPERPARAMS_VALUES = self.d.pop('hyperparameters')

        # Sbatch Parameter von sonstigen trennen:
        for param in self.sbatch_params_names:
            if self.d.__contains__(param):
                self.SBATCH_PARAMS[param] = self.d.get(param)
                self.d.pop(param)

        # Formatierung der Hyperparameter Eingaben x -> [x] etc.
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

        # single_to_set(ADDITIONAL_PARAMS)# FALLS ZUSÄTZLICHE PARAMETER EINBEZOGEN WERDEN SOLLEN: , **ADDITIONAL_PARAMS

        def product_dict(dictionary):
            keys = dictionary.keys()
            vals = dictionary.values()
            for instance in itertools.product(*vals):
                yield dict(zip(keys, instance))

        # ENTHÄLT DANN ALLE HYPERPARAMETER KOMBINATIONEN
        for item in (list(product_dict(
                self.HYPERPARAMS_VALUES))):  # FALLS ZUSÄTZLICHE PARAMETER EINBEZOGEN WERDEN SOLLEN: , **ADDITIONAL_PARAMS
            self.dicts.append(item)

        self.ADDITIONAL_PARAMS = self.d

    def run_batch_files(self):
        slurmrunnerpath = self.pathfinder('slurm_runner.py')
        i = 0
        if "output" in self.SBATCH_PARAMS:
            self.SBATCH_PARAMS["output"] = os.getcwd() + "/" + self.SBATCH_PARAMS["output"]
        for combination in self.dicts:
            with open('config' + str(i) + '.txt', 'w') as cf:
                cf.write(self.TESTPROBLEM + "\n")
                cf.write(self.OPTIMIZER + "\n")
                cf.write(str(combination) + "\n")
                cf.write(str(self.ADDITIONAL_PARAMS) + "\n")
                if self.OPTIMIZER_MODULE:
                    cf.write(self.OPTIMIZER_MODULE + "\n")
                if self.OPTIMIZER_PATH is not 'torch.optim':
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

