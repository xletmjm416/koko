#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:
    Mikolaj Metelski
"""
from abc import ABC, abstractmethod
from helpers import map_nested
from collections import ChainMap
import analytics


class AbstractModel(ABC):
    @abstractmethod
    def __init__(self, **params):
        # TODO call init calibrators here
        pass

    @abstractmethod
    def __call__(self, *model_input):
        pass

    @property
    def model_tree(self) -> dict:
        """Return model dependency tree whose leaves are primitive parameters
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

    @property
    def submodels(self):
        """List of first-level non-private submodels of a model object.
        """
        return [
            p for p_name, p in self.__dict__.items()
            if isinstance(p, AbstractModel) and not p_name.startswith("_")
        ]

    def get_submodels_of_type(self, type_):
        """Return first-level submodels of a certain type. Used in calibrators discovery.
        """
        return filter(lambda x: isinstance(x, type_), self.submodels)

    def __setattr__(self, name, value):
        try:
            # will raise if field name is not present in the top-level model
            val = getattr(self, name)
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
            |-a=3 # a is in the top level for the tree
            |-B=4
            | |-a=True # another occurence of a with different value
            | +-b=False
            |-C
            | |-a=SomeObject(a=5, b=7) # another occurence here
            | +-d=SomeObject(a=5, b=4) # a is inside an object that is a parameter
            
            >>> A.reparam(a=6)
            A
            |-a=6 # this is the one changed when A.a = 6
            |-B=4
            | |-a=6 # replaces all occurences
            | +-b=False
            |-C
            | |-a=6 # replaces all occurences
            | +-d=SomeObject(a=5, b=4) # SomeObject does not inherit from AbstractModel
            ```
        
        Returns:
            dict: dict with True/False on leaves where parameters were replaced
        """
        def func(leaf, path):
            current_value = leaf
            # last element of path is the parameter name
            param_name = path[-1]
            if param_name in parameters and not param_name.startswith("_"):
                node = self
                for step in path[:-1]:
                    # traverse the path but this time get the leaf object reference
                    # it won't raise as long as nothing changed in the tree since our call to get_model_tree
                    # TODO: prove this will never raise
                    node = getattr(node, step)
                setattr(node, param_name, parameters[param_name])
                return True  # place true at the leaf if parameter was updated
            return False  # place false if parameter was not updated

        # propagate reparam change only if the parameter already exists in the model tree
        return map_nested(func, self.model_tree)

    def run(self, *model_input, save=True):
        """Run model on model input and optionally save the model output.
        
        Args:
            model_input (Any): self-explanatory
            save (bool, optional): should the model output be saved (incl. parameters used and pickled model object)?
                Defaults to True. Internally uses `analytics.run_and_pickle`.
        
        Returns:
            Any: model output
        """
        calibrated_params = self._run_calibrators(*model_input, save)
        self.reparam(**calibrated_params)
        if save:
            return analytics.run_and_pickle(self, *model_input)
        else:
            return self(*model_input)

    def _run_calibrators(self, *model_input, save=True):
        # call submodel calibrators
        calibrators = self.get_submodels_of_type(Calibrator)
        params_to_update = [
            calibrator(self, *model_input) for calibrator in calibrators
        ]
        return dict(ChainMap(*params_to_update))


class Calibrator(AbstractModel):
    pass


if __name__ == "__main__":
    pass
