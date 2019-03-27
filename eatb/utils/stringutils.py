import re
import unittest


def lstrip_substring(instr, substr):
    """
    Remove substring from string at the beginning
    :param instr: original string
    :param substr: substring
    :return: result string
    """
    if instr.startswith(substr):
        len_substr = len(substr)
        return instr[len_substr:]
    else:
        return instr


def safe_path_string(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to underscore.
    """
    import unicodedata
    import re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '_', value)


def multiple_replacer(*key_values):
    import re
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)


def multiple_replace(string, *key_values):
    return multiple_replacer(*key_values)(string)


def whitespace_separated_text_to_dict(textmap):
    result_map = {}
    for line in textmap.splitlines():
        line = line.strip()
        if line:
            columns = line.rsplit(' ', 1)
            entry = {columns[0].strip(): columns[1].strip()}
            result_map.update(entry)
    return result_map
