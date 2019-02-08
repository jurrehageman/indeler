#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Practicum Assigner
by Jurre Hageman (with a little help from Dave Langers on the algorithm)
Year: 2018
License: GNU General Public License (GPL)
Date: 2018-12-19
"""
# Imports
import sys
import numpy as np
import random
import time
import argparse
import csv
import operator
from scipy.optimize import linear_sum_assignment
import collections

# Set numpy to print entire arrays
np.set_printoptions(threshold=np.inf)


def get_comm_args():
    """
    Reads command line arguments
    :return: object with command line arguments (obj)
    """
    parser = argparse.ArgumentParser(
        description="Select students in groups based on preferences")
    parser.add_argument("infile",
                        help="the path to the File with preferences")
    parser.add_argument("outfile",
                        help="the path to the File with the output")
    parser.add_argument("experiment_names",
                        help="path to the File with experiment info")
    args = parser.parse_args()
    return args


def read_file(file_name):
    """
    Reads student preferences csv file
    :param file_name: The name of the input file (str)
    :return: a list of dictionaries with student data.
    Each student is a dictionary (list)
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
                    'achternaam': line[2],
                    'voornaam': line[3],
                    'klas': line[4],
                    'thema': line[5],
                    'datum': line[6],
                    'tijd': line[7],
                    'voorkeuren': []
                }
                done.append(line[1])
            student_data['voorkeuren'].append(int(line[-1]))
    students.append(student_data)
    return students


def read_experiment_data(file_name):
    """
    reads the experiment data file and number of positions available
    :param file_name: The name of the experiment data file (str)
    :return: a list of dictionaries with experiment data.
    Each experiment is a dictionary. (list)
    """
    with open(file_name) as f:
        exp = []
        for line in f:
            line = line.strip().split(';')
            exp.append({'name': str(line[-1]),
                        'capacity': int(line[0])})
    return exp


def generate_pref_matrix(students):
    """
    generates preference matrix
    :param students: a list of dictionaries.
    Each student is a dictionary. (list)
    :return: matrix: a list of lists (preferences).
    Preferences are stored in a list. (list)
    """
    matrix = []
    for student in students:
        matrix.append(student['voorkeuren'])
    return matrix


def gen_exp_matrix(matrix, exp_data):
    """
    Extents an experiment matrix with preferences
    according to number of positions
    :param matrix: a list of lists with preferences (list)
    :param exp_data: a list of dictionaries with experiment data.
    Each experiment is a dictionary (list)
    :return: numpy array of the matrix.
    The matrix is expanded with "random preferences" (np_array)
    """
    exp_matrix = []
    num_of_students = len(matrix)
    total_exp_places = sum([i['capacity'] for i in exp_data])
    if total_exp_places < num_of_students:
        mssg = "Warning! {} experiment places < {} student places"
        print(mssg.format(total_exp_places, num_of_students))
        print("Exit...")
        sys.exit(1)
    for item in matrix:
        # generate list with None for each position
        student_matrix = [None for i in range(len(exp_data))]
        # add preferences at the positions:
        # exp   1   2   3   4   5   6
        # Jan           1   2       3
        # Piet      2       3   1
        # etc
        for index, i in enumerate(item):
            student_matrix[i - 1] = (index + 1)
        # now share remainder of preferences
        # generate numbers of remaining pref positions
        position_list = [i for i in range(len(item) + 1, len(exp_data) + 1)]
        # now fill the list with these numbers
        for index, item in enumerate(student_matrix):
            if item is None:
                random_exp = random.choice(position_list)
                student_matrix[index] = random_exp
                position_list.remove(random_exp)
        # now expand this list
        exp_list = []
        for index, item in enumerate(student_matrix):
            capacity = exp_data[index]['capacity']
            pos = [item for i in range(capacity)]
            exp_list += pos
        exp_matrix.append(exp_list)
    return np.array(exp_matrix)


def gen_assignment(expanded_matrix, experiment_data):
    """
    Generates an assignment using the Scipy linear sum assignment module
    :param expanded_matrix: numpy array of the matrix (np.array)
    :return: a list of selected_experiments (list)
    """
    experiment_row = []
    for num, item in enumerate(experiment_data):
        experiment_row += [num + 1 for i in range(item['capacity'])]
    row_ind, col_ind = linear_sum_assignment(expanded_matrix)
    selected_experiments = [experiment_row[i] for i in col_ind]
    return selected_experiments


def add_assign_data(student_data, assignment, exp_data):
    """
    Adds the assignment data to the student dictionary
    :param student_data: a list of dictionaries.
    Each student is a dictionary. (list)
    :param assignment: a list of selected_experiments (list)
    :return: list of students. each student is a dictionary (list)
    """
    for num, student in enumerate(student_data):
        student['assigned'] = assignment[num]
        name = exp_data[assignment[num] - 1]['name']
        student['assigned_exp_name'] = name
        if assignment[num] in student['voorkeuren']:
            selector = student['voorkeuren'].index(assignment[num]) + 1
            student['pref_position'] = selector
        else:
            student['pref_position'] = 'random'
    return student_data


def calc_assign_statistics(student_data, exp_data):
    """
    Calcs number of first choice, second choice etc.
    Calcs an assignment score: first choice: points = num of experiments,
    second choice: points = num of experiments -1.
    Prints results to screen
    :param student_data: list of students. each student is a dictionary (list)
    :param exp_data: a list of dictionaries with experiment data.
    Each experiment is a dictionary (list)
    :return: None
    """
    score = 0
    assigned = []
    print("Number of students: {}".format(len(student_data)))
    print()
    for student in student_data:
        assigned.append(student['assigned'])
        if student['pref_position'] != 'random':
            score += len(exp_data) - (student['pref_position'] - 1)
    ass_freq = collections.Counter(assigned)
    for i in sorted(ass_freq):
        capacity = exp_data[i - 1]['capacity']
        mssg = "experiment: {}, capacity: {}, assigned: {}, left over: {}"
        print(mssg.format(i, capacity, ass_freq[i], capacity - ass_freq[i]))
    print()
    for i in range(len(student_data[0]['voorkeuren'])):
        num_at_pos = [student['pref_position'] for student in student_data
                      if student['pref_position'] == i + 1].count(i + 1)
        print('Preference {}: {}'.format(i + 1, num_at_pos))

    print('Random: {}'.format(
        [student['pref_position']
         for student in student_data
         if student['pref_position'] == 'random'].count('random')))
    print()
    print('Total Score: {}'.format(score))


def write_results(student_data, outfile):
    """
    Write results to outfile using csv module
    :param student_data: list of students. each student is a dictionary (list)
    :param outfile: The name of the outfile (str)
    :return: None
    """
    with open(outfile, 'w') as f:
        writer = csv.writer(f, delimiter=';',
                            quotechar='"',
                            quoting=csv.QUOTE_ALL)
        student_data = sorted(student_data,
                              key=operator.itemgetter('achternaam'))
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
    Main module
    :return: 0 if OK
    """
    t0 = time.time()
    args = get_comm_args()
    student_data = read_file(args.infile)
    pref_matrix = generate_pref_matrix(student_data)
    exp_data = read_experiment_data(args.experiment_names)
    exp_matrix = gen_exp_matrix(pref_matrix, exp_data)
    assignment = gen_assignment(exp_matrix, exp_data)
    student_data = add_assign_data(student_data, assignment, exp_data)
    calc_assign_statistics(student_data, exp_data)
    write_results(student_data, args.outfile)
    print("Result written to {}".format(args.outfile))
    print("Approximate runtime:", round(time.time() - t0, 2), "sec")
    print("Done...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
