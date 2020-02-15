#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:
    Mikolaj Metelski
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
    pass
