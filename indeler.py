#!/usr/bin/env python3
"""
Practicum Assigner
by Jurre Hageman (with a little help from David Langers on the algorithm)
2018
Licence: GNU General Public License (GPL)
"""
#Imports
import sys
import numpy as np
import random
import time
import argparse
import csv
import operator
from scipy.optimize import linear_sum_assignment
import collections

#Set numpy to print entire arrays
np.set_printoptions(threshold=np.inf)


def get_comm_args():
    """
    reads command line arguments
    :return: args
    """
    parser = argparse.ArgumentParser(description="Select students in groups based on preferences")
    parser.add_argument("infile", help="the path to the File with preferences")
    parser.add_argument("outfile", help="the path to the File with the output")
    parser.add_argument("experiment_names", help="the path to the File with the names of experiments")
    args = parser.parse_args()
    return args


def read_file(file_name):
    """
    reads student preferences csv file
    :param file_name:
    :return: students
    """
    done = []
    students = []
    student_data = {}
    with open(file_name) as f:
        for line in f:
            line = line.strip().split('\t')
            if line[1] not in done:
                if student_data:
                    students.append(student_data)
                    done.pop(0)
                student_data = {
                    'student_num': int(line[1]),
                    'achternaam' : line[2],
                    'voornaam' : line[3],
                    'klas' : line[4],
                    'thema' : line[5],
                    'datum' : line[6],
                    'tijd' : line[7],
                    'voorkeuren' : []
                }
                done.append(line[1])
            student_data['voorkeuren'].append(int(line[-1]))
    students.append(student_data)
    return students


def read_experiment_data(file_name):
    """
    reads the experiment data file and number of positions available
    :param file_name:
    :return:
    """
    with open(file_name) as f:
        experiments = []
        for line in f:
            line = line.strip().split(';')
            experiments.append({'name' : str(line[-1]),
                                'capacity' : int(line[0])})
    return experiments


def generate_pref_matrix(students):
    """
    generates preference matrix
    :param students:
    :return: matrix
    """
    matrix = []
    for student in students:
        matrix.append(student['voorkeuren'])
    return matrix


def generate_experiment_matrix(matrix, experiment_data):
    """
    extents an experiment matrix with preferences according to number of positions
    :param matrix:
    :return: numpy array of the matrix
    """
    experiment_matrix = []
    num_of_students = len(matrix)
    total_experiment_places = sum([i['capacity'] for i in experiment_data])
    if total_experiment_places < num_of_students:
        print("Warning! only {} experiment places is less then number of students ({})".format(total_experiment_places, num_of_students))
        print("Exit...")
        sys.exit(1)
    for item in matrix:
        possible_experiments = list(range(1, len(experiment_data) + 1))
        student_matrix = [None for i in range(len(experiment_data))]
        for index, i in enumerate(item):
            student_matrix[i-1]= (index + 1)
        #now share remainder of preferences
        position_list = [i for i in range(len(item) + 1, len(experiment_data) + 1)]
        for index, item in enumerate(student_matrix):
            if item == None:
                random_experiment = random.choice(position_list)
                student_matrix[index] = random_experiment
                position_list.remove(random_experiment)

        #now expand this list
        expanded_list = []
        for index, item in enumerate(student_matrix):
            capacity = experiment_data[index]['capacity']
            expanded_list.append(capacity * str(item))
        expanded_list = [int(i) for j in expanded_list for i in j]
        experiment_matrix.append(expanded_list)
    return np.array(experiment_matrix)


def generate_assignment(expanded_matrix, experiment_data):
    """
    generates an assignment using the Scipy linear sum assignment module
    :param expanded_matrix:
    :return:
    """
    experiment_capacity = [i['capacity'] for i in experiment_data]
    experiment_row = [str((i + 1)) * experiment_capacity[i] for i in range(len(experiment_capacity))]
    experiment_row_separated = [int(i) for j in experiment_row for i in j]
    row_ind, col_ind = linear_sum_assignment(expanded_matrix)
    selected_experiments = [experiment_row_separated[i] for i in col_ind]
    return selected_experiments


def add_assignment_data(student_data, assignment, experiment_data):
    """
    adds the assignment data to the student dictionary
    :param student_data:
    :param assignment:
    :return: list of student data dictionaries
    """
    for num, student in enumerate(student_data):
        student['assigned'] = assignment[num]
        name = experiment_data[assignment[num]-1]['name']
        student['assigned_exp_name'] = name
        if assignment[num] in student['voorkeuren']:
            student['pref_position'] = student['voorkeuren'].index(assignment[num])+1
        else:
            student['pref_position'] = 'random'
    return student_data


def calc_assignment_statistics(student_data, experiment_data):
    """
    calcs number of first choice, second choice etc.
    calcs an assignment score: first choice: points = num of experiments, second choice: points = num of experiments -1 etc.
    :param student_data:
    :return:
    """
    score = 0
    assigned = []
    print("Number of students: {}".format(len(student_data)))
    print()
    for student in student_data:
        assigned.append(student['assigned'])
        if student['pref_position'] != 'random':
            score += len(experiment_data) - (student['pref_position'] -1)
    assigned_frequencies = collections.Counter(assigned)
    for i in sorted(assigned_frequencies):
        capacity = experiment_data[i-1]['capacity']
        print("experiment: {}, capacity: {}, assigned: {}, places left over: {}".format(i, capacity, assigned_frequencies[i], capacity - assigned_frequencies[i]))
    print()
    for i in range(len(student_data[0]['voorkeuren'])):
        num_at_position = [student['pref_position'] for student in student_data if student['pref_position'] == i+1].count(i+1)
        print('Preference {}: {}'.format(i+1, num_at_position))

    print('Random: {}'.format([student['pref_position'] for student in student_data if student['pref_position'] == 'random'].count('random')))
    print()
    print('Total Score: {}'.format(score))


def write_results(student_data, outfile):
    """
    write results to outfile using csv module
    :param student_data:
    :param outfile:
    :return:
    """
    with open(outfile, 'w') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        student_data = sorted(student_data, key=operator.itemgetter('achternaam'))
        for student in student_data:
            row = [student['achternaam'],
                   student['voornaam'],
                   student['student_num'],
                   student['klas'],
                   student['klas'],
                   student['thema'],
                   student['datum'],
                   student['tijd'],
                   student['voorkeuren'],
                   student['pref_position'],
                   student['assigned'],
                   student['assigned_exp_name']]
            writer.writerow(row)


def main():
    """
    main module
    :return: 0 if OK
    """
    t0 = time.time()
    args = get_comm_args()
    student_data = read_file(args.infile)
    pref_matrix = generate_pref_matrix(student_data)
    experiment_data = read_experiment_data(args.experiment_names)
    experiment_matrix = generate_experiment_matrix(pref_matrix, experiment_data)
    assignment = generate_assignment(experiment_matrix, experiment_data)
    student_data = add_assignment_data(student_data, assignment, experiment_data)
    calc_assignment_statistics(student_data, experiment_data)
    write_results(student_data, args.outfile)
    print("Result written to {}".format(args.outfile))
    print("Approximate runtime:", round(time.time()-t0, 2), "sec")
    print("Done...")
    return 0


if __name__ == "__main__":
    sys.exit(main())