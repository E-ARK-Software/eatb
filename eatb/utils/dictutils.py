import re

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def dict_keys_underscore_to_camel(d):
    d_new = {}
    for k, _ in d.items():
        d_new[underscore_to_camel(k)] = d[k]
    return d_new


def dict_keys_camel_to_underscore(d):
    d_new = {}
    for k, _ in d.items():
        d_new[camel_to_underscore(k)] = d[k]
    return d_new
