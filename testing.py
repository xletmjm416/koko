#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:
    Mikolaj Metelski
"""
import unittest

import numpy as np

from analytics import (calibrate_on_param_grid, calibrate_on_run_results,
                       pickle_sweep_results, run_and_pickle, run_on_param_grid)
from core import AbstractModel, Calibrator


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


class NestedModel(AbstractModel):
    def __init__(self, alpha: float, model: AbstractModel):
        self.alpha = alpha
        self.model = model

    def __call__(self, data: float) -> float:
        return max(self.alpha, self.model(self.alpha))


class NestedModelWithCalibrator(AbstractModel):
    def __init__(self, alpha: float, calibrator: Calibrator):
        self.alpha = alpha
        self.calibrator = calibrator

    def __call__(self, model_input: float) -> float:
        return model_input + self.alpha


class FooCalibrator(Calibrator):
    def __init__(self):
        pass

    def __call__(self, model_object, model_input):
        return {'alpha': 8}


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.foo_model = FooModel(3)
        self.bar_model = BarModel(3, [1, 2, 3])
        self.nested_model = NestedModel(5, FooModel(3))
        self.nested_model_with_calibrator = NestedModelWithCalibrator(
            5, FooCalibrator())

    def test_init(self):
        self.assertRaises(TypeError, AbstractModel)

    def test_FooBarModel(self):
        self.assertEqual(self.foo_model(5), 5)
        self.assertEqual(self.foo_model(2), 3)
        self.assertEqual(self.bar_model(5), 5)
        self.assertEqual(self.bar_model(2), 3)

    def test_run_on_param_grid(self):
        run_on_param_grid(BarModel,
                          3,
                          number=[-1, 0, 1],
                          arr=[[1, 2, 3], [-1, 2, 5]])
        # TODO add assertions

    def test_calibrate_on_param_grid(self):
        calibrate_on_param_grid(BarModel,
                                3,
                                target=lambda x, y: y**2,
                                number=[-1, 0, 1],
                                arr=[[1, 2, 3], [-1, 2, 5]])
        # TODO add assertions

    def test_calibrate_on_run_results(self):
        run_results = run_on_param_grid(BarModel,
                                        3,
                                        number=[-1, 0, 1],
                                        arr=[[1, 2, 3], [-1, 2, 5]])
        calibrate_on_run_results(run_results, target=lambda x, y: y**2)

    def test_model_tree(self):
        # check for raises
        A = self.foo_model.model_tree
        B = self.nested_model.model_tree
        # A == {'parameter': 3}
        # B == {'alpha': 3, 'model': {parameter: 3}}]}
        pass

    def test_reparam(self):
        g = self.nested_model.reparam(parameter=5)
        # g == {'alpha': 3, 'model': {parameter: 5}}]}
        pass

    def test_pickle_sweep_results(self):
        run_results = run_on_param_grid(BarModel,
                                        3,
                                        number=[-1, 0, 1],
                                        arr=[[1, 2, 3], [-1, 2, 5]])
        self.assertRaises(NotImplementedError, pickle_sweep_results, run_results)
        # TODO add assertions

    def test_AbstractModel_run(self):
        model_output_1 = self.foo_model.run(3)
        model_output_2 = self.nested_model.run(3)

    def test_submodels(self):
        nested_model_submodels = self.nested_model.submodels

    def test_run_calibration(self):
        # modelobject.__call__ will not call submodel calibrators
        model_output = self.nested_model_with_calibrator(5)
        self.assertEqual(model_output, 10)
        # modelobject.run will call the submodel calibrators
        model_output_run = self.nested_model_with_calibrator.run(5)
        self.assertEqual(model_output_run, 13)


class Mass(object):
    def __init__(self, magnitude, position):
        self.magnitude = magnitude
        self.position = position

    def __mul__(self, other):
        if isinstance(other, float):
            return self.magnitude * other
        elif isinstance(other, Mass):
            return self.magnitude * other.magnitude


class NewtonianGravityModel():
    def __init__(self, gravitational_constant=6.67e-11):
        self.gravitational_constant = gravitational_constant

    def __call__(self, mass1: Mass, mass2: Mass) -> float:
        distance = np.abs(mass1.position - mass2.position)
        return ((self.gravitational_constant * (mass1 * mass1)) /
                (distance)**2)


class NewtonianGravityTest(unittest.TestCase):
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
        a_vs_b = self.model_a(self.mass_a, self.mass_b)
        self.assertEqual(a_vs_b, 8e-11)
        b_vs_c = self.model_a(self.mass_b, self.mass_c)
        self.assertEqual(b_vs_c, 2e-11)


if __name__ == "__main__":
    unittest.main()
