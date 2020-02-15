#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import Mapping
from itertools import product


def map_nested(func, node, path=[]):
    """Walk on a dictionary as a tree and call `func` on
    each leaf.

    Args:
        func: callable taking two arguments: the leaf and the path to it
            (path as list)
        node (collections.Mapping): the tree
        path: (for recursive use only)
    Returns:
        nested dict, on leaved of type returned by func.

    Source:
        https://stackoverflow.com/questions/32935232/python-apply-function-to-values-in-nested-dictionary
    """
    new_path = path.copy()
    if isinstance(node, Mapping):
        for k, v in node.items():
            return {
                k: map_nested(func, v, new_path + [k])
                for k, v in node.items()
            }
    else:
        return func(node, new_path)


def product_of_dicts(**kwargs):
    """Cartesian product of dictionaries.

    Args:
        kwargs: dictionary of lists

    Returns:
        list of dictionaries containing combinations of key-value pairs
        given in elements of kwargs.

    Source:
        https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists
    """
    keys = kwargs.keys()
    vals = kwargs.values()
    for instance in product(*vals):
        yield dict(zip(keys, instance))
