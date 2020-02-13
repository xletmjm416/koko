#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:author: Mikolaj Metelski
"""
from abc import ABC, abstractmethod

class AbstractModel(ABC):
    
    @abstractmethod
    def __init__(self, *params):
        pass
    
    @abstractmethod
    def __call__(self, *data):
        pass

if __name__ == "__main__":
    # manual test; put into a unit test
    try:
        model = AbstractModel()
    except TypeError:
        print("ok")