# Assigner

Get the best assignment out of student preferences for a project.
Uses the Munkres algorithm:
https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linear_sum_assignment.html

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Scipy and numpy need to be installed on your system


### Installing

Use pip to install scipy and numpy:
Numpy:

```
sudo pip install numpy
```

Scipy

```
sudo pip install scipy
```


## Running the generate_dummy_data.py module

This module will generate some dummy data to test

Example:
```
python3 generate_dummy_data.py my_file.csv
```

### It has some optional arguments:

usage: generate_dummy_data.py [-h] [-s STUDENTS] [-p PREFERENCES]
                              [-e EXPERIMENTS]
                              outfile

Required argument:
outfile: the name of the outfile

Optional arguments:
STUDENTS: number of students (defaults 100)
PREFERENCES: number of preferences (defaults 3)
EXPERIMENTS: number of experiments (defaults 8)


## Running the assignment.py module

This module will generate the actual assignment

Example:
```
python3 assigner.py test_prefs.csv test_assignment.csv experiment_data.txt
```

usage: assigner.py [-h] infile outfile experiment_names

Required argument:
infile: path to the csv file containing the preferences
outfile: path to the csv file with the assignment
experiment_names: a txt file with number of positions and the name of the experiments

## Built With

* [Scipy linear sum assignment module](https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linear_sum_assignment.html)


## Contributing



## Versioning



## Authors

* **Jurre Hageman** - (https://github.com/jurrehageman/indeler)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

Dave Langers helped on the algorithm