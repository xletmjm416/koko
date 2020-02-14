#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:author: Mikolaj Metelski
"""

from collections import defaultdict
from collections import Mapping
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


def map_nested(func, node, path=[]):
    """Walk on a dictionary as a tree and call `func` on
    each leaf.

    Args:
        func: callable taking two arguments: the leaf and the path to it
            (path as list)
        node (collections.Mapping): the (sub)tree
        path: (for recursive use only)
    Returns:
        nested dict, on leaved of type returned by func.
    
    Source:
        https://stackoverflow.com/questions/32935232/python-apply-function-to-values-in-nested-dictionary
    """
    new_path = path.copy()
    if isinstance(node, Mapping):
        for k, v in node.items():
            return {k: map_nested(func, v, new_path + [k])
                for k, v in node.items()}
    else:
        return func(node, new_path)

def product_of_dicts(**kwargs):
    """Cartesian product of dictionaries.
    Args:
        kwargs: dictionary of lists
    Returns:
        list of dictionaries containing combinations of key-value pairs given in elements of kwargs.
    Source: https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists"""
    keys = kwargs.keys()
    vals = kwargs.values()
    for instance in product(*vals):
        yield dict(zip(keys, instance))


def run_on_param_grid(model, data, **params_ranges):
    """Run model on grid of its params.
    
    If you just want to run the model (on one set of 
    parameters and one dataset), use `model(**params)(data)` instead.
    
    Pass the arguments
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
        . Input validation
        . Use recursive_dict/fix the key convention
        . do not rely on key ordering
        . if you don't pass a list, fix value and not show up in results as separate key

    Args:
        model: inherits from AbstractModel
        data: model will be called with the same data
            for each parameter combination
        params_ranges: keyword arguments of the model with lists of values
    Returns:
        dict: key is a tuple made from a combination of params,
            val is the result of the run
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
    return calibrate_on_run_results(results, target)


def calibrate_on_run_results(results, target):
    """Pick a set of parameters that minimises target given the results of run_on_param_grid. 
    If you don't have the run results, use calibrate_on_param_grid instead.

    Todo:
        Input validation

    Args:
        results: returned from run_on_param_grid
        target: a function that accepts two positional arguments: parameters used in the model (as a stringified dict) and a possible model output.
    See:
        calibrate_on_param_grid
        run_on_param_grid
    """
    optimal_param_set = min({k: target(k, v) 
        for k, v in results.items()},
        key=results.get)
    return optimal_param_set, results.get(optimal_param_set)
