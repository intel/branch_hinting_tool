#!/usr/bin/env python

__author__ = 'GabrielCSMO'
import os
import sys

def folder(Path):
    old_path = os.getcwd()
    os.chdir(Path)
    lista = os.listdir(".")
    for item in lista:
        if os.path.isdir(item):
            folder(item)
            print item
        else:
            pass
    os.chdir(old_path)
    print old_path
folder(sys.argv[1])