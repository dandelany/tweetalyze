import csv, copy
from pprint import pprint
from inspect import getargspec
from decorator import decorator
from prettytable import PrettyTable

"""
This module contains decorators used by the functions in helpers.py
"""

@decorator
def export_csv(f, *args, **kwargs):
    result = f(*args, **kwargs)
    
    filename = kwarg_lookup('export_csv', f, args)
    if filename and type(result) is list and len(result):
        # if passed a 1D array, make a 2D array with 1 item/line
        result_copy = False
        if type(result[0]) is not list: 
            result_copy = [[row] for row in result]
        else:
            result_copy = result
        # create CSV file
        new_file = open(filename + '.csv','wb')
        csv_writer = csv.writer(new_file)
        for row in result_copy:
            csv_writer.writerow(row)
        new_file.close()

    return result

@decorator
def print_table(f, *args, **kwargs):
    result = f(*args, **kwargs)
    
    print_table = kwarg_lookup('print_table', f, args)
    if print_table and type(result) is list and len(result):
        # if passed a 1D array, make a 2D array with 1 item/line
        result_copy = False
        if type(result[0]) is not list: 
            result_copy = [[row] for row in result]
        else:
            result_copy = result
        # create and print pretty table
        table = PrettyTable(result_copy[0])
        for row in result_copy[1:]:
            table.add_row(row)
        print table

    return result

@decorator
def should_return(f, *args, **kwargs):
    result = f(*args, **kwargs)
    # conditional return
    should_return = kwarg_lookup('should_return', f, args)
    if(should_return):
        return result
    else:
        return

def kwarg_lookup(keyword, func, args):
    try:
        return args[getargspec(func).args.index(keyword)]
    except:
        return False