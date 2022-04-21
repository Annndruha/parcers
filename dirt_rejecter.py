import os
import re
import sys
import base64
import argparse

import nbformat


def count_dirt(notebook):
    # Global meta
    if notebook["metadata"] != nbformat.NotebookNode():
        ctr["metadata"] += 1

    # Cell meta and others
    for cell in notebook['cells']:
        if 'execution_count' in cell:
            if cell["execution_count"] is not None:
                if cell["execution_count"] != 0:
                    ctr["execution_count"] += 1
        if cell["metadata"] != nbformat.NotebookNode():
            ctr["metadata"] += 1
        if 'outputs' in cell:
            if cell["outputs"] != list():
                ctr["outputs"] += 1


def process_one_lecture(pathname, backup):
    lecture_path = os.path.dirname(pathname)
    notebook_name = os.path.basename(pathname)
    notebook = nbformat.read(pathname, as_version=nbformat.NO_CONVERT)

    # Count how many meta, outs and outputs
    count_dirt(notebook)

    return ctr.is_notebook_dirty()


class Counter(dict):
    def __init__(self):
        super().__init__()
        self["metadata"] = 0
        self["outputs"] = 0
        self["execution_count"] = 0

    def summary(self):
        if sum(list(self.values())) == 0:
            print("\tMy congratulations, notebook is perfect!")
        else:
            if self['metadata'] != 0:
                print(f"\tMetadata fixes: {self['metadata']}")
            if self['outputs'] != 0:
                print(f"\tOutputs fixes: {self['outputs']}")
            if self['execution_count'] != 0:
                print(f"\tExecution counts fixes: {self['execution_count']}")

    def reset(self):
        self.__init__()

    def is_notebook_dirty(self):
        if sum(list(self.values())) == 0:
            return False
        else:
            return True


def main():
    if args.filepath is not None:
        lecture_pathname = args.filepath
        if lecture_pathname.endswith('.ipynb'):
            ctr.reset()
            res = process_one_lecture(lecture_pathname, backup=args.backup)
            if res:
                sys.exit(f"Found dirty lecture: {lecture_pathname}\nPleace, clear it by cleaner.py")
                # ctr.summary()
    else:
        dirty_lectures = []
        for path, subdirs, files in os.walk(args.root if args.root is not None else "."):
            for name in files:
                if name.endswith('.ipynb') and \
                        ".ipynb_checkpoints" not in path and \
                        not name.endswith('_backup.ipynb'):
                    lecture_pathname = os.path.join(path, name)
                    ctr.reset()
                    res = process_one_lecture(lecture_pathname, backup=args.backup)
                    if res:
                        dirty_lectures.append(lecture_pathname)
                    # ctr.summary()
            if args.root is None:
                break
        if len(dirty_lectures) != 0:
            sys.exit(f"Found dirty lectures:\n\t" + "\n\t".join(dirty_lectures)+'\nPlease, clear it by cleaner.py')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for cleaning notebooks.')
    parser.add_argument('--backup', dest='backup', action='store_true',
                        help="If provided, create a ipynb backup.")
    parser.add_argument('--disable-warnings', dest='warnings', action='store_false',
                        help="Script disable warnings like 'Probably local link found.'")
    parser.add_argument('--filepath', default=None,
                        help='Notebook filepath, if not provided, script processed all files in root, if root '
                             'not provided, processed all file in current directory.')
    parser.add_argument('--root', default=None,
                        help="""(default:"None") Processed all file in root folder and all subfolders.""")
    parser.set_defaults(backup=False)
    parser.set_defaults(warnings=True)

    args = parser.parse_args()
    ctr = Counter()
    main()
