import os


def add_event(task, outcome, identifier_value,  linking_agent, package_premis_file, ip_work_dir):
    """
    Update premis file
    :param task:
    :param outcome:
    :param identifier_value:
    :param linking_agent:
    :param package_premis_file:
    :param ip_work_dir:
    :return:
    """
    package_premis_file.add_event(task, outcome, identifier_value, linking_agent)
    path_premis = os.path.join(ip_work_dir, "metadata/PREMIS.xml")
    with open(path_premis, 'w') as output_file:
        output_file.write(package_premis_file.to_string())
    print('PREMIS file updated: %s' % path_premis)
