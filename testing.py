#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:author: Mikolaj Metelski
"""
from core import AbstractModel


class Foo(AbstractModel):
    def __init__(self, parameter: float):
        self.parameter = parameter

    def __call__(self, data: float) -> float:
        return max(data, self.parameter)


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
