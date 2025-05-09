# -*- coding: utf-8 -*-

def split_namespace(path: str) -> (str, str):
    strs = path.split(":")
    return strs[0], strs[1]

def get_namespace(path: str) -> str:
    return split_namespace(path)[0]
