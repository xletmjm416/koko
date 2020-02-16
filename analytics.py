#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:
    Mikolaj Metelski
"""

import json
import pathlib
import pickle
import uuid
from typing import Any, Dict, List, Tuple, Union

import helpers
from core import AbstractModel


def run_on_param_grid(model: Union[AbstractModel.__class__, AbstractModel],
                      data: Any, **params_ranges: Dict[str, Any]):
    """Run model on grid of its params.

    If you just want to run the model (on one set of
    parameters and one dataset), use `model(**params)(data)` instead.

    If you pass a model object as `model`, it will call `model.reparam(**new_parameters)`
    for each point on the grid. If you pass a class inheriting from `AbstractModel` instead,
    it will create the models from scratch every time. This may be very important if your `model.__init__`
    and `model.__call__` have different calibration procedures, or when the model depends on the history
    of its reparametrisation. 

    Pass the arguments of the model as keyword arguments with list values.

    Examples:

        >>> class MyModel(AbstractModel):
        >>>    ...
        >>> run_on_param_grid(MyModel, mydata, a=[1, 2], b=[True, False])

        will run the following models on mydata:

        >>> MyModel(a=1, b=True)(mydata)
        >>> MyModel(a=2, b=True)(mydata)
        >>> MyModel(a=1, b=False)(mydata)
        >>> MyModel(a=2, b=False)(mydata)

        But this code:

        >>> sample_model = MyModel(a=5, b=6)
        >>> run_on_param_grid(sample_model, mydata, a=[1, 2], b=[True, False])

        will run the following models on mydata:

        >>> sample_model.reparam(a=1, b=True)
        >>> sample_model(mydata)
        >>> sample_model.reparam(a=2, b=True)
        >>> sample_model(mydata)
        >>> sample_model.reparam(a=1, b=False)
        >>> sample_model(mydata)
        >>> sample_model.reparam(a=2, b=False)
        >>> sample_model(mydata)

    Todo:
        [ ] Input validation
        [-] Use recursive_dict/fix the key convention
        [x] do not rely on key ordering
        [ ] if you don't pass a list, fix value and do
            not show up in results as separate key
        [ ] parallelize

    Args:
        model (Union[AbstractModel.__class__, AbstractModel]): inherits from AbstractModel or is a model object itself
        data (Any): model will be called with the same data
            for each parameter combination
        params_ranges: keyword arguments of the model with lists of values

    Returns:
        (type): dict of run label - tuple pairs. first elemnt of tuple is parameters, second - model output.
    """
    def inner(params):
        run_uuid = uuid.uuid4()
        if isinstance(model, AbstractModel.__class__):
            run_label = '_'.join([model.__name__, str(run_uuid)])
            return {run_label: (params, model(**params)(data))}
        elif isinstance(model, AbstractModel):
            run_label = '_'.join([model.__class__.__name__, str(run_uuid)])
            model.reparam(**params)
            return {run_label: (params, model(data))}
        else:
            raise TypeError(
                "can only pass class inheriting from AbstractModel or an object of such class as model"
            )

    # TODO parallelize here
    from collections import ChainMap
    return dict(
        ChainMap(*map(inner, helpers.product_of_dicts(**params_ranges))))


def calibrate_on_param_grid(model, data, target, **params_ranges):
    """Run the model on a parameter grid and pick a set of parameters
    that minimises `target`.

    If you already called run_on_param_grid and have the results,
    use calibrate_on_run_results instead.

    Todo:
        [ ] Input validation

    Args:
        model: inherits from AbstractModel
        data: model will be called with the same data
            for each parameter combination
        target: a function that accepts two positional arguments:
            parameters used in the model (as a stringified dict) and
            a possible model output.
        params_ranges: keyword arguments of the model with
            lists of values

    Returns:
        dict: key is a tuple made from a combination of params

    See:
        calibrate_on_run_results
    """
    results = run_on_param_grid(model, data, **params_ranges)
    return calibrate_on_run_results(results, target)


def calibrate_on_run_results(results, target):
    """Pick a set of parameters that minimises target
    given the results of run_on_param_grid.

    If you don't have the run results, use calibrate_on_param_grid instead.

    Todo:
        [ ] Input validation

    Args:
        results: returned from run_on_param_grid
        target: a function that accepts two positional arguments:
            parameters used in the model (as a stringified dict) and
            a possible model output.

    See:
        calibrate_on_param_grid
        run_on_param_grid
    """
    map_target = {label: target(*pair) for label, pair in results.items()}
    optimal_run_label = min(map_target, key=map_target.get)
    return optimal_run_label, results.get(optimal_run_label)


def run_and_pickle(model_object: AbstractModel, model_input: Any) -> None:
    """Run model object on model input and save results in a pickle file.

    By default, saves the model output in './out/Model-uuid' folder
    together with the pickled model object and a json of the model tree.
    
    Args:
        model_object (AbstractModel): self-explanatory
        model_input (Any): self-explanatory
    
    Returns:
        None
    """
    run_label = '_'.join([model_object.__class__.__name__, str(uuid.uuid4())])
    model_output = model_object(model_input)
    out_path = pathlib.Path("./out") / run_label
    path = out_path.mkdir(parents=True, exist_ok=False)
    with (out_path / "parameters.json").open("w+") as file:
        json.dump(model_object.model_tree, file)
    with (out_path / "model_output.pickle").open("wb+") as file:
        pickle.dump(model_output, file)
    return model_output


def pickle_sweep_results(results):
    """Pickle results of run_on_param_grid.
    
    By default, a model output is saved as './out/Model-uuid' format.
    
    Args:
        results: output from Model(**parameter_input)(model_input).
    """
    raise NotImplementedError
    for label, param, model_output in results:
        out_path = pathlib.Path("./out") / label

        path = out_path.mkdir(parents=True, exist_ok=False)
        with (out_path / "parameters.json").open("w+") as file:
            json.dump(param, file)
        with (out_path / "output.pickle").open("wb+") as file:
            pickle.dump(model_output, file)
