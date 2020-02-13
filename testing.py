#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:author: Mikolaj Metelski
"""
from core import AbstractModel
from analytics import run_on_param_grid


class Foo(AbstractModel):
    def __init__(self, parameter: float):
        self.parameter = parameter

    def __call__(self, data: float) -> float:
        return max(data, self.parameter)

class Bar(AbstractModel):
    def __init__(self, number: float, arr: list):
        self.number = number
        self.arr = arr

    def __call__(self, data: float) -> float:
        return max(self.number, max(data, max(self.arr)))

if __name__ == "__main__":
    # manual test; put into a unit test
    try:
        model = AbstractModel()
    except TypeError:
        print("ok")
    # manual test; put into a unit test
    model = Foo(3)
    assert model(5) == 5
    assert model(2) == 3
    # manual test; put into a unit test
    model = Bar(3, [1, 2, 3])
    assert model(5) == 5
    assert model(2) == 3
    # manual test; put into a unit test
    model = Bar(3, [1, 2, 3])
    print(run_on_param_grid(Bar,
                            3,
                            number=[-1, 0, 1],
                            arr=[[1, 2, 3], [-1, 2, 5]]))
