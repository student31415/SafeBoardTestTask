#!/usr/bin/env python
import json
import os
import re
import shutil
import time

import yaml
import datetime
# import cerberus
DEBUG = True
# def validate(obj):
#     v = cerberus.Validator(schema)
#     res =  v.validate(obj)
#     # print(json.dumps(v.document_error_tree['type'], indent=2))
#     print(v.errors)
#     return

def split_rules(rules):
    dir_rules, file_rules = [], []
    for rule in rules:
        if rule['type'] == 'dir':
            dir_rules.append(rule)
        else:
            file_rules.append(rule)
    return dir_rules, file_rules

def is_release(dir_name):
    versions = dir_name.split('.')
    if len(versions) != 4:
        return None
    if int(versions[2]) / 10 > 0:
        return False
    else:
        return True

def check_assembly(assembly_type, file_name):
    return (assembly_type == 'release') == is_release(file_name)

def older(days, file_path):
    if days is None:
        return True
    now = datetime.datetime.fromtimestamp(time.time())
    then = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
    delta = datetime.timedelta(days=days)
    return then + delta < now

def match_regex(regexp, file_name):
    res = re.match(regexp, file_name)
    return res is not None


def iterate_over_files(path, rules):
    if path[-1] != '/':
        path += "/"

    files = os.listdir(path)

    for file in files:
        if os.path.isdir(path + file):
            iterate_over_files(path+file, rules)
        else:
            for rule in rules:
                if match_regex(rule['mask'], file) and older(rule.get('older_in_days'), path+file):
                    if DEBUG:
                        print(f'delete {path + file}')
                    else:
                        os.remove(path+file)
                    break


def iterate_over_dirs(path, rules):
    if path[-1] != '/':
        path += "/"

    files = os.listdir(path)

    for file in files:
        if os.path.isdir(path + file):
            for rule in rules:
                # print(f'{path+file: <20}, ass {check_assembly(rule["assembly_type"], file)}, old {older(rule.get("older_in_days"), path + file)}')
                if (
                        check_assembly(rule["assembly_type"], file)         # check assembly type
                        and older(rule.get("older_in_days"), path + file)   # check if file is old enough
                ):
                    if DEBUG:
                        print(f'delete {path+file}')
                    else:
                        shutil.rmtree(path+file)
                    break




def main():
    path = ''
    rules = []

    with open("config.yaml") as file:
        yml = yaml.load(file, Loader=yaml.Loader)
        # print(json.dumps(yml, indent=2) )
        path = yml['path']
        rules = yml['rules']

    dir_rules, file_rules = split_rules(rules)
    iterate_over_dirs(path, dir_rules)
    iterate_over_files(path, file_rules)


if __name__ == '__main__':
    main()
