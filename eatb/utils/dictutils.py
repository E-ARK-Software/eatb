import re

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def dict_keys_to_underscore_to_camel(d):
    for k, _ in d.items():
        d[underscore_to_camel(k)] = d.pop(k)
    return d


d = {'publisher': 'test', 'publisher_email': 'testprovider@eark-project.com', 'language': 'English', 'processId': 'cfc1b56d-7223-4316-a9c5-631dd96fe3d0', 'currdate': '2020-03-24T23:43:34Z', 'date': '24.03.2020', 'last_change': '2020-03-24T23:43:33Z', 'tags': '[]', 'userGeneratedTags': '[]', 'contactPoint': 'test', 'contactEmail': 'testprovider@eark-project.com', 'created': '2020-03-24T23:43:33Z', 'landingPage': 'http://localhost:8000/iprepo/access/package/cfc1b56d-7223-4316-a9c5-631dd96fe3d0/', 'title': 'test', 'description': 'test'}

print(dict_keys_to_underscore_to_camel(d))