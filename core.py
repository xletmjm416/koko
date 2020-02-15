#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:
    Mikolaj Metelski
"""
from abc import ABC, abstractmethod
from analytics import map_nested


class AbstractModel(ABC):
    @abstractmethod
    def __init__(self, *params):
        pass

    @abstractmethod
    def __call__(self, *data):
        pass

    def get_model_tree(self):
        """Traverse model dependency tree whose leaves are non-AbstractModel parameters
        of the model.
        
        Returns:
            dict: the tree in dict format
        """
        def func(leaf, path):
            if isinstance(leaf, AbstractModel):
                return leaf.__dict__
            else:
                return leaf

        return map_nested(func, self.__dict__.copy())


if __name__ == "__main__":
    pass
