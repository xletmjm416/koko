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
    def __init__(self, **params):
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

    def __setattr__(self, name, value):
        try:
            val = getattr(
                self, name
            )  # will raise if field name is not present in the top-level model
            if isinstance(val, AbstractModel):
                # do something
                raise NotImplementedError(
                    "complete replacing of dependent models is not yet supported"
                )
            else:
                return super().__setattr__(name, value)
        except:
            # fallback on the default setattr
            return super().__setattr__(name, value)

    def reparam(self, **parameters) -> dict:
        """Propagate reparametrisation to all leaves of the model tree.
        
        The expected behaviour of `model.param = 5` is to set the parameter value
        at the top level of the model. `reparam` instead replaces all occurences
        of the parameters in the leaves of the model tree with values.

        If the leaf is an object, its `setattr` will *not* be called but the object replaced
        altogether.

        Examples:
            uppercase letters inherit from AbstractModel, lowercase do not.
            ```
            >>> print_tree(A) # printtree is not yet implemented
            A
            |-a=3
            |-B=4
            | |-a=True # another occurence of a with different value
            | +-b=False
            +-C
            |-g=5
            |-E
            | +-d=SomeObject(a=5, b=4) # d does not inherit from AbstractModel
            |-D
            | +-g=5
            +-F
            
            >>> A.reparam(a=6)
            A
            |-a=6
            |-B=4
            | |-a=6 # replaces all occurences
            | +-b=False
            +-C
            |-g=5
            |-E
            | +-d=SomeObject(a=5, b=4) # d does not inherit from AbstractModel
            |-D
            | +-g=5
            +-F
            ```
        
        Returns:
            dict: dict with True/False on leaves where parameters were replaced
        """
        # propagate reparam change only if the parameter already exists in the model tree
        tree = self.get_model_tree()

        def func(leaf, path):
            current_value = leaf
            # last element of path is the parameter name
            param_name = path[-1]
            if param_name in parameters:
                node = self
                for step in path[:-1]:
                    # traverse the path but this time get the leaf object reference
                    # it won't raise as long as nothing changed in the tree since our call to get_model_tree
                    # TODO: prove this will never raise
                    node = getattr(node, step)
                setattr(node, param_name, parameters[param_name])
                return True  # place true at the leaf if parameter was updated
            return False  # place false if parameter was not updated

        return map_nested(func, tree)


if __name__ == "__main__":
    pass
