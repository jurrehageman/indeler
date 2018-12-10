#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate dummy data for munkres indeler
by Jurre Hageman
Year: 2018
License: GNU General Public License (GPL)
"""
# Imports
import random
import sys
import argparse
import datetime
import time
import csv


def get_comm_args():
    """
    Reads command line arguments
    :return: object with command line arguments
    """
    parser = argparse.ArgumentParser(description="Generate dummy data")
    parser.add_argument("outfile", help="the path to the File with the output")
    parser.add_argument("-s", "--students", type=int,
                        help="change number of students, defaults 100")
    parser.add_argument("-p", "--preferences", type=int,
                        help="change number of preferences, defaults 3")
    parser.add_argument("-e", "--experiments", type=int,
                        help="change number of experiments, defaults 8")
    args = parser.parse_args()
    return args


def generate_dummy_data_file(file_name, num_of_students, experiments, preferences):
    """
    Generates csv file which can be used in indeler.py
    :param file_name: The name of the file (str)
    :param num_of_students: The number of students (int)
    :param experiments: The number of experiments (int)
    :param preferences: The number of preferences (int)
    :return: None
    """
    with open(file_name, "w") as f:
        writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        student_num = 300001
        for student in range(num_of_students):
            entry = student + 1
            first_name = "voornaam {}".format(str(entry).zfill(len(str(num_of_students-1))))
            last_name = "achternaam {}".format(str(entry).zfill(len(str(num_of_students-1))))
            group = "BOVR2B"
            theme = 5
            date_now = datetime.datetime.today().strftime('%Y-%m-%d')
            time_now = time.strftime("%H:%M:%S")
            choices = random.sample(range(1, experiments+1), preferences)
            for line in range(preferences):
                row = [entry,
                       student_num,
                       last_name,
                       first_name,
                       group,
                       theme,
                       date_now,
                       time_now,
                       line+1,
                       entry,
                       line+1,
                       choices[line]
                       ]
                writer.writerow(row)
            student_num += 1


def main():
    """
    The main module
    :return: returns 0 if OK
    """
    students = 100
    preferences = 3
    experiments = 8
    arguments = get_comm_args()
    if arguments.students not None:
        students = arguments.students
    if arguments.preferences not None:
        preferences = arguments.preferences
    if arguments.experiments not None:
        experiments = arguments.experiments
    generate_dummy_data_file(arguments.outfile, students, experiments, preferences)
    print("Students:", students)
    print("Preferences:", preferences)
    print("Experiments:", experiments)
    print("Data written to {}".format(arguments.outfile))
    return 0


if __name__ == "__main__":
    sys.exit(main())
