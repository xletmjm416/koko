#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:
    Mikolaj Metelski
"""

from typing import Any, Union

import helpers
from core import AbstractModel


def run_on_param_grid(
        model: Union[AbstractModel.__class__, AbstractModel], data: Any,
        **params_ranges: dict[str, Any]) -> List[Tuple[dict, Any]]:
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
        ```
        >>> class MyModel(AbstractModel):
        >>>    ...
        >>> run_on_param_grid(MyModel, mydata, a=[1, 2], b=[True, False])
        ```
        will run the following models on mydata:
        ```
        MyModel(a=1, b=True)(mydata)
        MyModel(a=2, b=True)(mydata)
        MyModel(a=1, b=False)(mydata)
        MyModel(a=2, b=False)(mydata)
        ```

        ```
        >>> sample_model = MyModel(a=5, b=6)
        >>> run_on_param_grid(sample_model, mydata, a=[1, 2], b=[True, False])
        ```
        will run the following models on mydata:
        ```
        sample_model.reparam(a=1, b=True)
        sample_model(mydata)
        sample_model.reparam(a=2, b=True)
        sample_model(mydata)
        sample_model.reparam(a=1, b=False)
        sample_model(mydata)
        sample_model.reparam(a=2, b=False)
        sample_model(mydata)
        ```

    Todo:
        [ ] Input validation
        [-] Use recursive_dict/fix the key convention
        [x] do not rely on key ordering
        [ ] if you don't pass a list, fix value and do
            not show up in results as separate key
    Args:
        model (Union[AbstractModel.__class__, AbstractModel]): inherits from AbstractModel or is a model object itself
        data (Any): model will be called with the same data
            for each parameter combination
        params_ranges: keyword arguments of the model with lists of values
    
    Returns:
        List[Tuple[dict, Any]]: list of tuples made from a combination of params, val is the result of the run
    """
    def inner(params):
        if isinstance(model, AbstractModel.__class__):
            return (params, model(**params)(data))
        elif isinstance(model, AbstractModel):
            model.reparam(**params)
            return (params, model(data))
        else:
            raise TypeError(
                "can only pass class inheriting from AbstractModel or an object of such class as model"
            )

    return map(inner, helpers.product_of_dicts(**params_ranges))


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
    optimal_param_set = min({k: target(k, v)
                             for k, v in results},
                            key=results.get)
    return optimal_param_set, results.get(optimal_param_set)
