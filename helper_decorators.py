import csv, copy
from pprint import pprint
from datetime import datetime
from inspect import getargspec
from decorator import decorator
from prettytable import PrettyTable

"""
This module contains decorators used by the functions in helpers.py
"""
@decorator
def date_range(f, *args, **kwargs):
    begin_date = kwarg_lookup('begin_date', f, args)
    end_date = kwarg_lookup('end_date', f, args)
    extend_query_index = kwarg_index('extend_query', f, args)

    if (begin_date or end_date) and extend_query_index:
        date_query = {'created_at': {}}

        if begin_date:
            # parse date if it's a string
            if type(begin_date) is str:
                date_list = begin_date.split('/')
                begin_date = datetime(int(date_list[2]), int(date_list[0]), int(date_list[1]))
            # add to date query
            date_query['created_at']['$gte'] = begin_date

        if end_date:
            # parse date if it's a string
            if type(end_date) is str:
                date_list = end_date.split('/')
                end_date = datetime(int(date_list[2]), int(date_list[0]), int(date_list[1]))
            # add to date query
            date_query['created_at']['$lte'] = end_date

        # add the date range to the extend_query keyword argument
        extend_query = dict(args[extend_query_index].items() + date_query.items())
        # by slicing it into the args tuple :P
        args = args[:extend_query_index] + (extend_query,) + args[extend_query_index+1:]

    result = f(*args, **kwargs)
    return result

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

def kwarg_index(keyword, func, args):
    try:
        return getargspec(func).args.index(keyword)
    except:
        return False