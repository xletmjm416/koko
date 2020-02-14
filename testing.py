#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:author: Mikolaj Metelski
"""
from core import AbstractModel
from analytics import \
    run_on_param_grid, \
    calibrate_on_param_grid, \
    calibrate_on_run_results
import numpy as np
import unittest

class FooModel(AbstractModel):
    def __init__(self, parameter: float):
        self.parameter = parameter

    def __call__(self, data: float) -> float:
        return max(data, self.parameter)

class BarModel(AbstractModel):
    def __init__(self, number: float, arr: list):
        self.number = number
        self.arr = arr

    def __call__(self, data: float) -> float:
        return max(self.number, max(data, max(self.arr)))

class Mass(object):
    def __init__(self, magnitude, position):
        self.magnitude = magnitude
        self.position = position

    def __mul__(self, other):
        return self.magnitude * other.magnitude


class NewtonianGravityModel():
    def __init__(self, gravitational_constant=6.67e-11):
        self.gravitational_constant = gravitational_constant

    def __call__(self, mass1: Mass, mass2: Mass) -> float:
        distance = np.abs(mass1.position - mass1.position)
        return ((self.gravitational_constant * mass1 * mass1) /
                (distance) ** 2)


class NewtonianGravityUnittest(unittest.TestCase):
    def setUp(self):
        self.model_a = NewtonianGravityModel(gravitational_constant=8e-11)
        self.model_b = NewtonianGravityModel(gravitational_constant=6e-6)
        self.mass_a = Mass(1.0, 0.0)
        self.mass_b = Mass(1.0, 1.0)
        self.mass_c = Mass(1.0, -1.0)
        self.mass_d = Mass(-1.0, 0.0)
        self.mass_e = Mass(-1.0, 1.0)


    def test_init(self):
        model = NewtonianGravityModel(gravitational_constant=8e-11)
        self.assertEqual(model.gravitational_constant, 8e-11)


    def test_call(self):
        a_vs_b = model(self.mass_a, self.mass_b)
        self.assertEqual(a_vs_b, 8e-11)
        b_vs_c = model(self.mass_b, self.mass_c)
        self.assertEqual(b_vs_c, 8e-11)



if __name__ == "__main__":
    unittest.main()
    # manual test; put into a unit test
    try:
        model = AbstractModel()
    except TypeError:
        print("ok")
    # manual test; put into a unit test
    model = FooModel(3)
    assert model(5) == 5
    assert model(2) == 3
    # manual test; put into a unit test
    model = BarModel(3, [1, 2, 3])
    assert model(5) == 5
    assert model(2) == 3
    # manual test; put into a unit test
    model = BarModel(3, [1, 2, 3])
    print(run_on_param_grid(BarModel,
                            3,
                            number=[-1, 0, 1],
                            arr=[[1, 2, 3], [-1, 2, 5]]))
    # manual test; put into a unit test
    model = BarModel(3, [1, 2, 3])
    print(calibrate_on_param_grid(BarModel, 3, target=lambda x: x**2,
                                  number=[-1, 0, 1],
                                  arr=[[1, 2, 3], [-1, 2, 5]]))
    # manual test; put into a unit test
    model = BarModel(3, [1, 2, 3])
    run_results = run_on_param_grid(Bar, 3, number=[-1, 0, 1], arr=[[1, 2, 3], [-1, 2, 5]])
    print(calibrate_on_run_results(run_results, target=lambda x: x**2))
