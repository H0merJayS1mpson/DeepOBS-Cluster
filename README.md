# Deepobs for TCML Cluster

Interface for Deeobs on TCML-Cluster

## Getting Started

Copy Folder into your Cluster /home/usr_name folder. Or copy files into folder of your choice.

### Prerequisites

TCML-CLuster Account.

### Running the Interface

First you will need to generate a Configuration ```.txt``` file. 
It contains the following:

```
Testprobmlem Name - See Deepobs Documentation for available Testproblems
Optimizer class Name - Name of the optimizer Class
Optimizer Path - Path to where the optimizer is stored
Optimizer module - Module description in Python import style
Set of Hyperparameters for the Optimizer - Hyperparamters which should be tested (every Combination will get tested)
Additional Paramters for Deeobs Trainingphase - See Deepobs Documentation for Details
Sbatch Parameters - Sbatch Parameters used for the configurations
```

Entries should generally be structured like this:

```
key: value
```

For example it could look like this:

```
Testproblem: mnist_mlp
Optimizer: name_of_optimzer_class
Optimizer Path: /home/usr_name/user_optimizer/user_optimizer_file.py
Optimizer Module: user_optimizer.user_optimizer_file.name_of_optimzer_class
lr: (0.01, 0.05, 0.01)
momentum: [0.99, 0.79]
nesterov: False
num_epochs: 1
batch_size: 200
sbatch_job_name: The_jobs_name
sbatch_nnodes: 1
sbatch_ntasks: 1
sbatch_cpus_per_task: 5
sbatch_gres: gpu:1080ti:1
sbatch_partition: test
sbatch_time: 15:00
output: user_specified_outputfolder

```



## For Infos on Deepobs see:

* [Deepobs Documentation](https://deepobs.readthedocs.io/en/v1.2.0-beta0/) - The DNN Optimizer Benchmark suite


## Acknowledgments

* Hat tip to anyone whose code was used
* etc
