#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ortools.sat.python import cp_model
import time
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

import math

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


PRINT_INTERMEDIATE_SOLUTIONS = True



class VarArrayAndObjectiveSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.start = time.time()
        self.start_interval = time.time()

    def on_solution_callback(self):
        t1 = time.time()
        time_used = t1 - self.start
        interval_used = t1 - self.start_interval
        self.start_interval = t1
        print('Interval using %.4f, Accu using %.4f, Solution %i' % (interval_used, time_used, self.__solution_count), end = ', ')
        print('objective value = %i' % self.ObjectiveValue())

        self.__solution_count += 1
        if PRINT_INTERMEDIATE_SOLUTIONS:
            solution = [0]*len(self.__variables[0])
            for f in range(len(self.__variables)):
                for c in range(len(self.__variables[0])):
                    if self.Value(self.__variables[f][c]) == 1:
                        solution[c] = f
            print(solution)

    def solution_count(self):
        return self.__solution_count



def solve(facilities, customers, max_minutes = 150, initial_sol = None):

    model = cp_model.CpModel()

    x = [[0] * len(customers) for _ in range(len(facilities))]
    for f in facilities: #row
        for c in customers: #col
            x[f.index][c.index] = model.NewBoolVar('x_%s_%s'%(f.index, c.index))

    # capacity constraint
    for f in facilities:
        model.Add(
            sum(x[f.index][c.index]*c.demand for c in customers) <= f.capacity
        )
    # each customers rewired to exactly one facility
    for c in customers:
        model.Add(
            sum(x[f.index][c.index] for f in facilities) == 1
        )
    
    if initial_sol is not None:
        for c, f in enumerate(initial_sol):
            model.AddHint(x[f][c], 1)
    
    used = [0] * len(facilities)
    for f in facilities:
        used[f.index] = model.NewBoolVar('used{}'.format(f.index))
        model.AddMaxEquality(used[f.index], x[f.index])

    # objective function
    obj = 0
    for f in facilities: #row
        obj += f.setup_cost * used[f.index]
        for c in customers: #col
            obj += x[f.index][c.index] * length(f.location, c.location)

    model.Minimize(obj)
    
    # solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60*max_minutes
    solution_printer = VarArrayAndObjectiveSolutionPrinter(x)
    status = solver.SolveWithSolutionCallback(model, solution_printer)
    print('----------------')
    print('Status       : %s' % solver.StatusName(status))
    print('#sol found   : %i' % solution_printer.solution_count())
    print('Branches     : %i' % solver.NumBranches())
    print('Wall time    : %f s' % solver.WallTime())

    obj = solver.ObjectiveValue()
    solution = [0]*len(x[0])
    for f in range(len(x)):
        for c in range(len(x[0])):
            if solver.Value(x[f][c]) == 1:
                solution[c] = f

    print("objective value: ", obj)
    print("solution: ", solution)

    return solution