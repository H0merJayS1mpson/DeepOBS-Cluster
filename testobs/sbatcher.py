#!/usr/bin/python
import os
import sys
import subprocess
from string import Template


# class sBatcher():
#     BATCH_FILE_TEMPLATE = None
#     RUN_FILE_TEMPLATE = os.getcwd()
#     FILE_DIRECTORY = os.getcwd()
#     WORKPATH = os.getcwd()  # os.path.dirname(os.path.realpath(sys.argv[0]))[11:]  # 11 to remove /mnt/beegfs
#     OUTPUT_DIRECTORY = os.getcwd() + "/output"
#     default_sbatch_params = {
#         "sbatch_job_name": "default_experiment_name",
#         "sbatch_nnodes": 1,
#         "sbatch_ntasks": 1,
#         "sbatch_cpus_per_task": 5,
#         "sbatch_mem_per_cpu": "10G",
#         "sbatch_gres": "gpu:1080ti:1",
#         "sbatch_partition": "test",
#         "sbatch_time": "15:00",
#         # "minutes:seconds", "hours:minutes:seconds", "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
#         "output": os.getcwd() + "/output"
#     }
# 
#     default_entry_file_path = os.getcwd()
# 
#     def __init__(self, config_file_path, sbatch_params=default_sbatch_params, entry_file_path=default_entry_file_path,
#                  dataset_to_copy_path=default_entry_file_path, batch_template=os.getcwd() + "/batch_template.tmp"):
#         self.entry_file_path = entry_file_path
#         self.config_file_path = config_file_path
#         self.dataset_to_copy_path = dataset_to_copy_path
#         self.sbatch_params = sbatch_params
#         for key in self.default_sbatch_params:
#             if key not in self.sbatch_params:
#                 self.sbatch_params[key] = self.default_sbatch_params[key]
#         self.OUTPUT_DIRECTORY = self.sbatch_params["output"]
#         self.BATCH_FILE_TEMPLATE = batch_template

def pathfinder(filename, directory="./"):
    command = "find"
    directory = directory
    flag = "-iname"
    fn = filename
    args = [command, directory, flag, fn]
    process = subprocess.run(args, stdout=subprocess.PIPE)
    path = process.stdout.decode().strip("\n")
    head, sep, tail = path.partition('\n')
    return head

class sBatcher():
    BATCH_FILE_TEMPLATE = None
    RUN_FILE_TEMPLATE = os.getcwd()
    FILE_DIRECTORY = os.getcwd()
    WORKPATH = os.getcwd()  # os.path.dirname(os.path.realpath(sys.argv[0]))[11:]  # 11 to remove /mnt/beegfs
    OUTPUT_DIRECTORY = os.getcwd() + "/output"
    default_sbatch_params = {
        "sbatch_job_name": "default_experiment_name",
        "sbatch_nnodes": 1,
        "sbatch_ntasks": 1,
        "sbatch_cpus_per_task": 5,
        "sbatch_mem_per_cpu": "10G",
        "sbatch_gres": "gpu:1080ti:1",
        "sbatch_partition": "test",
        "sbatch_time": "15:00",
        # "minutes:seconds", "hours:minutes:seconds", "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
        "output": os.getcwd() + "/output"
    }

    default_entry_file_path = os.getcwd()

    def __init__(self, config_file_path, sbatch_params=default_sbatch_params, entry_file_path=default_entry_file_path,
                 dataset_to_copy_path=default_entry_file_path):
        self.entry_file_path = entry_file_path
        self.config_file_path = config_file_path
        self.dataset_to_copy_path = dataset_to_copy_path
        self.sbatch_params = sbatch_params
        for key in self.default_sbatch_params:
            if key not in self.sbatch_params:
                self.sbatch_params[key] = self.default_sbatch_params[key]
        self.OUTPUT_DIRECTORY = self.sbatch_params["output"]
        head = pathfinder("batch_template.tmp")
        self.BATCH_FILE_TEMPLATE = head
        

    # Template:
    # experiment_name="test"
    # optimizer="SGD"
    # experiment_name = "test"
    # optimizer = "SGD"
    # grid_search_params = {
    #     "model": ["resnet"],
    #     "training_steps": [1000],
    #     "batch_size": [1, 2],
    #     "train_data_size": [2000],
    #     "random_seed": [1],
    #     "num_gpus": [1],
    #     "optimizer_args": {"learning_rate": [1, 2], "momentum": [3, 4]},
    #     "decay_args": {"decay_rate": [23]},
    #     "additional": {"test": [2]}
    # }

    def run_configurations(self, i):
        """
        starts a slurm job for each run
        :param runs: list of type :class:`Run`
        """
        if not os.path.exists(self.OUTPUT_DIRECTORY):
            os.makedirs(self.OUTPUT_DIRECTORY)
        #        if not os.path.exists(self.FILE_DIRECTORY):
        #            os.makedirs(self.FILE_DIRECTORY)

        # generate batch files
        with open(self.BATCH_FILE_TEMPLATE) as batchTemp:
            file = batchTemp.read()
        t = Template(file)
        batchcontent = t.substitute(runfile=self.entry_file_path, experiment_name=self.sbatch_params['sbatch_job_name'],
                                    configfile=self.config_file_path, **self.sbatch_params)
        batch_file_path = self.FILE_DIRECTORY + '/' + self.sbatch_params['sbatch_job_name'] + "_" + str(i) + ".sbatch"
        with open(batch_file_path, "w+") as batchfile:
            batchfile.write(batchcontent)
        batchfile.close()
        # os.system(f"chmod 775 " + f"'" + batch_file_path + f"'")
        # os.system("sbatch " + batch_file_path)





    # Template:
    # experiment_name="test"
    # optimizer="SGD"
    # experiment_name = "test"
    # optimizer = "SGD"
    # grid_search_params = {
    #     "model": ["resnet"],
    #     "training_steps": [1000],
    #     "batch_size": [1, 2],
    #     "train_data_size": [2000],
    #     "random_seed": [1],
    #     "num_gpus": [1],
    #     "optimizer_args": {"learning_rate": [1, 2], "momentum": [3, 4]},
    #     "decay_args": {"decay_rate": [23]},
    #     "additional": {"test": [2]}
    # }

    def run_configurations(self, i):
        """
        starts a slurm job for each run
        :param runs: list of type :class:`Run`
        """
        if not os.path.exists(self.OUTPUT_DIRECTORY):
            os.makedirs(self.OUTPUT_DIRECTORY)
#        if not os.path.exists(self.FILE_DIRECTORY):
#            os.makedirs(self.FILE_DIRECTORY)

        # generate batch files
        with open(self.BATCH_FILE_TEMPLATE) as batchTemp:
            file = batchTemp.read()
        t = Template(file)
        batchcontent = t.substitute(runfile=self.entry_file_path, experiment_name=self.sbatch_params['sbatch_job_name'],
                                    configfile=self.config_file_path, **self.sbatch_params)
        batch_file_path = self.FILE_DIRECTORY+'/' + self.sbatch_params['sbatch_job_name'] + "_" + str(i) + ".sbatch"
        with open(batch_file_path, "w+") as batchfile:
            batchfile.write(batchcontent)
        batchfile.close()
        #os.system(f"chmod 775 " + f"'" + batch_file_path + f"'")
        #os.system("sbatch " + batch_file_path)
        

class cleaner():
    
    def __init__(self, runfile, experiment_name, job_dict):
        self.runfile = runfile
        self.experiment_name = experiment_name
        self.job_dict = job_dict
        
        
    
    def clean_up(self):
        
        head = pathfinder("temp.tmp")
        headremover = pathfinder("file_remover.py")
        headbatch = pathfinder("clean_up.sbatch")
        
        with open(head) as batchTemp:
            file = batchTemp.read()
        t = Template(file)
        batchcontent = t.substitute(runfile = headremover, experiment_name = self.experiment_name, job_dict = str(self.job_dict))
        batch_file_path = headbatch
        with open(batch_file_path, "w+") as batchfile:
            batchfile.write(batchcontent)
        batchfile.close()  
    
