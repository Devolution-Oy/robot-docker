#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import glob

#from glob import glob
from os.path import abspath, dirname, isdir, join as path_join
from os.path import split as path_split, splitext

from robot import run_cli           # use cli versions as you can pass cli
from robot.libdoc import libdoc_cli # arguments to them straight up


CURDIR = abspath(dirname(__file__))
LIBROOT = path_join(CURDIR, 'libs')
RESOURCEROOT = path_join(CURDIR, 'resources')
DOCROOT = path_join(CURDIR, 'docs')
ESCAPED_CURDIR = CURDIR.replace(' ', '!')
DEFAULT_ARGS = '--outputdir logs --escape space:! --variable PROJECTROOT:{root} {source}'.format(
    root=ESCAPED_CURDIR, source=path_join(ESCAPED_CURDIR, 'tests'))
DEFAULT_LIBS = ['BuiltIn', 'SeleniumLibrary', 'Process',
        'OperatingSystem', 'Dialogs', 'Collections', 'String', 'DateTime']

def extend_pythonpath(libroot):
    for dirname in os.listdir(libroot):
        path = path_join(libroot, dirname)
        if isdir(path):
           sys.path.insert(1, path)

def _create_docs_path(docroot, filepath):
    _, filename = path_split(filepath)
    filename, _ = splitext(filename)
    targetpath = filename + '.html'
    return path_join(docroot, targetpath)

def generate_doc(args):
    try:
        libdoc_cli(args)
    except SystemExit as e: # libdoc_cli calls sys.exit()
        if e.code != 0:
            raise
    print("---")

def generate_docs(orig_libdoc_args, libroot, resourceroot, docroot):
    libs = glob.glob(path_join(libroot, '**/[!_]*Library.py'), recursive=True)
    resources = glob.glob(path_join(resourceroot, '**/*.robot'),  recursive=True)

    lib_keywords_folder = path_join(docroot, 'library_keywords')
    if not os.path.exists(lib_keywords_folder):
        os.makedirs(lib_keywords_folder)

    for sourcefile in libs:
        used_libdoc_args = list(orig_libdoc_args) # reset arguments back
        targetpath = _create_docs_path(lib_keywords_folder, sourcefile)
        print('{} =>'.format(sourcefile))
        used_libdoc_args.extend([sourcefile, targetpath])
        generate_doc(used_libdoc_args)

    for default_library in DEFAULT_LIBS:
        used_libdoc_args = list(orig_libdoc_args) # reset arguments back
        targetpath = _create_docs_path(lib_keywords_folder, default_library)
        print('{} =>'.format(default_library))
        used_libdoc_args.extend([default_library, targetpath])
        generate_doc(used_libdoc_args)

    resource_keywords_folder = path_join(docroot, 'resource_keywords')
    if not os.path.exists(resource_keywords_folder):
        os.makedirs(resource_keywords_folder)

    for sourcefile in resources:
        used_libdoc_args = list(orig_libdoc_args) # reset arguments back
        targetpath = _create_docs_path(resource_keywords_folder, sourcefile)
        print('{} =>'.format(sourcefile))
        used_libdoc_args.extend([sourcefile, targetpath])
        generate_doc(used_libdoc_args)

def main(cli_args):
    extend_pythonpath(LIBROOT)
    if len(cli_args) > 0 and cli_args[0] == 'docs':
        return generate_docs(cli_args[1:], LIBROOT, RESOURCEROOT, DOCROOT)
    cli_args.extend(DEFAULT_ARGS.split())
    return run_cli(cli_args)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

