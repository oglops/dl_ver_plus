# class Utils(object):
import os

def _readFile(file):
    if os.path.isfile(file):
        with open(file) as f:
            content = f.read()
    else:
        content = None
    return content
