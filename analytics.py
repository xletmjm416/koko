#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:author: Mikolaj Metelski
"""

from collections import defaultdict
from itertools import product


def recursive_dict():
    return defaultdict(recursive_dict)


def set_recursive_item(val, recursive_dict, labels):
    raise NotImplementedError("do not use, untested")
    for idx, label in enumerate(labels):
        if idx == len(labels) - 1:
            recursive_dict[label] = val
        else:
            recursive_dict[label] = recursive_dict[labels[idx + 1]]


def walk_and_call(func, node, path=[]):
    """Walk on a dictionary as a tree and call `func` on
    each leaf.

    Args:
        func: callable taking two arguments: the leaf and the path to it
            (path as list)
        node: dictionary
        path: (for recursive use only)
    Returns:
        T: type of func's return
    """
    new_path = path.copy()
    if isinstance(node, dict):
        for label, item in node.items():
            walk_and_call(func, item, new_path)
    else:
        func(node, new_path)


def product_of_dicts(**kwargs):
    """Cartesian product of dictionaries.
    Args:
        kwargs: dictionary of lists
    Returns:
        list of dictionaries containing combinations of kwargs given.
    Source: https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists"""
    keys = kwargs.keys()
    vals = kwargs.values()
    for instance in product(*vals):
        yield dict(zip(keys, instance))


def run_on_param_grid(model, data, **params_ranges):
    """Run model on grid of its params. Pass the arguments
    of the model as keyword arguments with list values:
    ```
    run_on_param_grid(mymodel, mydata, a=[1, 2], b=[True, False])
    ```
    will run the following models on mydata:
    ```
    mymodel(a=1, b=True)(mydata)
    mymodel(a=2, b=True)(mydata)
    mymodel(a=1, b=False)(mydata)
    mymodel(a=2, b=False)(mydata)
    ```

    Todo:
        Input validation
        Use recursive_dict - do not rely on key ordering

    Args:
        model: inherits from AbstractModel
        data: model will be called with the same data
            for each parameter combination
        params_ranges: keyword arguments of the model with lists of values
    Returns:
        dict: key is a tuple made from a combination of params
    """
    results = dict()
    for params in product_of_dicts(**params_ranges):
        results[str(params)] = model(**params)(data)
    return results


def calibrate_on_param_grid(model, data, target, **params_ranges):
    """Run the model on a parameter grid and pick a set of parameters
    that minimises `target`.
    
    If you already called run_on_param_grid and have the results, use calibrate_on_run_results instead.

    Todo:
            Input validation

    Args:
        model: inherits from AbstractModel
        data: model will be called with the same data
            for each parameter combination
        target: a function that accepts two positional arguments: parameters used in the model (as a stringified dict) and a possible model output.
        params_ranges: keyword arguments of the model with 
            lists of values
    Returns:
        dict: key is a tuple made from a combination of params
    See:
        calibrate_on_run_results
    """
    results = run_on_param_grid(model, data, **params_ranges)
    return calibrate_on_run_results(results, target


def calibrate_on_run_results(results, target):
    """Pick a set of parameters that minimises target given the results of run_on_param_grid. If you don't have the run results, use
    calibrate_on_param_grid.
    target: a function that accepts two positional arguments: parameters used in the model (as a stringified dict) and a possible model output.
    See:
        calibrate_on_param_grid"""
    optimal_param_set = min({k: target(k, v) for k, v in results.items()}, key=results.get)
    return optimal_param_set, results.get(optimal_param_set)
