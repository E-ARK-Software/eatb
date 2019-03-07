#!/usr/bin/env python
# -*- coding: utf-8 -*-


def flatten_list(nested_list):
    for i in nested_list:
        if isinstance(i, (list, tuple)):
            for j in flatten_list(i):
                yield j
        else:
            yield i
