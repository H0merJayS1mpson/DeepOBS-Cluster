import os
import fnmatch
import sys
from ast import literal_eval
from subprocess import Popen, PIPE

experiment_name = sys.argv[1]

job_dict={}

with open(sys.argv[2], 'r') as f:
    d = f.read()
    job_dict = literal_eval(d)


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def remove_all(pattern, path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                os.remove(str(name))
                
remove_all('config*.txt', os.getcwd())
remove_all(experiment_name + '*.sbatch', os.getcwd())
remove_all('job_dict*.txt', os.getcwd())

for key in job_dict:
    stdout = Popen('sacct -j '+ key +' --format State', shell=True, stdout=PIPE).stdout
    output = stdout.read()
    out = output.decode("utf-8")
    is_failed = out.find('FAILED')
    if (is_failed > -1):
        with open(os.getcwd()+'/failed_configurations.txt', 'a') as fc:
            fc.write("Failed Job ID: " + key + ", corresponding configuration: " + str(job_dict[key]) + "\n")
            
with open(os.getcwd()+'/failed_configurations.txt', 'a') as fc:
    fc.write("\nPLEASE MAKE SURE TO DELETE THIS FILE BEFORE RE-RUNNING FAILED JOBS. REPEATEDLY FAILING JOBS WOULD GET ATTACHED TO THIS FILE! \n")
del(sys.argv[1])
del(sys.argv[1])

