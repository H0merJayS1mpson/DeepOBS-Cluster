#!/bin/bash

#SBATCH --job-name=clean-up

#resources:

#SBATCH --cpus-per-task=1
# the job can use and see 4 CPUs (from max 24).

#SBATCH --partition=test
# the slurm partition the job is queued to.

#SBATCH --mem-per-cpu=3G
# the job will need 12GB of memory equally distributed on 4 cpus.  (251GB are available in total on one node)

#SBATCH --gres=gpu:1
#the job can use and see 1 GPUs (4 GPUs are available in total on one node)

#SBATCH --time=00:30
# the maximum time the scripts needs to run
# "minutes:seconds", "hours:minutes:seconds", "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"



#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
##SBATCH --output=job.%J.out
##SBATCH --error=job.%J.err
# write the error output to job.*jobID*.err


#singularity exec --nv /common/singularityImages/TCML-Cuda10_0Tensorflow1_13v2.simg

srun python3 ./testobs/file_remover.py DER_JOB! /mnt/beegfs/home/hartert/job_dict.txt
echo DONE! DELETE clean_up.sbatch

