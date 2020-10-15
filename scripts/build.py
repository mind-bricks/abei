#!/usr/bin/env python

import os
import subprocess

if __name__ == '__main__':
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # cwd_pardir = os.path.dirname(cwd)
    # install dependencies
    subprocess.call([
        'pip',
        'install',
        '-r',
        'requirements-dev.txt',
    ], cwd=cwd)

    format_code_cmd = [
        'autopep8',
        '-r',
        '--in-place',
        '--aggressive',
        '--aggressive',
        '--max-line-length=79',
    ]
    subprocess.call([*format_code_cmd, 'abei'], cwd=cwd)
    subprocess.call(['flake8', 'abei'], cwd=cwd)

    subprocess.call([*format_code_cmd, 'tests'], cwd=cwd)
    subprocess.call(['flake8', 'tests'], cwd=cwd)

    subprocess.call([
        'python', '-m', 'unittest', 'tests'], cwd=cwd)
