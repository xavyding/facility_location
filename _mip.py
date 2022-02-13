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

from ortools.linear_solver import pywraplp
import math

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)



def solve(facilities, customers, max_minutes = 10):

    solver = pywraplp.Solver.CreateSolver('SCIP')

    x = [[0] * len(customers) for _ in range(len(facilities))]
    for f in facilities: #row
        for c in customers: #col
            x[f.index][c.index] = solver.IntVar(0, 1, 'x_%s_%s'%(f.index, c.index))
    

    # capacity constraint
    for f in facilities:
        solver.Add(
            sum(x[f.index][c.index]*c.demand for c in customers) <= f.capacity
        )
    # each customers rewired to exactly one facility
    for c in customers:
        solver.Add(
            sum(x[f.index][c.index] for f in facilities) == 1
        )
    
    used = [0] * len(facilities)
    
    for f in facilities:
        used[f.index] = solver.IntVar(0, 1, 'used{}'.format(f.index))
        for c in customers:
            solver.Add(
                used[f.index] >= x[f.index][c.index]
            )

    # objective function
    obj = 0
    for f in facilities: #row
        obj += f.setup_cost * used[f.index]
        for c in customers: #col
            obj += x[f.index][c.index] * length(f.location, c.location)

    solver.Minimize(obj)
    solver.SetTimeLimit(max_minutes*60000)
    status = solver.Solve()

    obj = solver.Objective().Value()

    print("optimal? ", status == pywraplp.Solver.OPTIMAL)
    solution = [0]*len(x[0])
    for f in range(len(x)):
        for c in range(len(x[0])):
            if x[f][c].solution_value() == 1:
                solution[c] = f
    
    print("objective value: ", obj)
    print("solution: ", solution)

    return solution