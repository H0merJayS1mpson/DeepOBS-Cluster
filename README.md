# Project Title

Interface for Deeobs on TCML-Cluster

## Getting Started

Copy Folder into your Cluster /home/usr_name folder. Or copy files into folder of your choice.

### Prerequisites

TCML-CLuster Account.
```
Give examples
```


```
Give examples
```

### Running the Interface

First you will need to generate a Configuration ```.txt``` file. 
Generally it has to be structured like this:

```
Testprobmlem Name - See Deepobs Documentation for available Testproblems
Optimizer class Name - Name of the optimizer Class
Optimizer Path - Path to where the optimizer is stored
Optimizer module - Module description in Python import style
Set of Hyperparameters for the Optimizer - Hyperparamters which should be tested (every Combination will get tested)
Additional Paramters for Deeobs Trainingphase - See Deepobs Documentation for Details
Sbatch Parameters - Sbatch Parameters used for the configurations
```


For example it could look like this:

```
Testproblem: mnist_mlp
Optimizer: SGD
Optimizer Path: /home/hartert/optimopti/optimopti.py
Optimizer Module: optimopti.optimopti.sgd
lr: [0.01, 0.02, hampelmann, sonstwie]
momentum: [0.99, 0.79]
nesterov: False
num_epochs: 1
batch_size: 200
sbatch_job_name: DER_JOB!
sbatch_nnodes: 1
sbatch_ntasks: 1
sbatch_cpus_per_task: 5
sbatch_gres: gpu:1080ti:1
sbatch_partition: test
sbatch_time: 15:00
output: DER_outputordner

```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

