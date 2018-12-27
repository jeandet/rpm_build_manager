#!/usr/bin/env python3

__author__ = "Alexis Jeandet"
__copyright__ = "Copyright 2017, Laboratory of Plasma Physics"
__credits__ = []
__license__ = "GPLv2"
__version__ = "1.0.0"
__maintainer__ = "Alexis Jeandet"
__email__ = "alexis.jeandet@member.fsf.org"
__status__ = "Development"

import subprocess, os
from termcolor import colored
from typing import Union


def listify(arg):
    return arg if type(arg) is list else [arg]


def generate_output_name(basename, timestamp):
    return basename+'_'+timestamp.isoformat().replace(':', '-')


def invoke(command: str, args: Union[list, str], stdout: object = subprocess.PIPE, stdin: object = subprocess.PIPE, shell=False, simulate: bool = False) -> subprocess.CompletedProcess:
    cmd = listify(command) + listify(args)
    new_env = dict(os.environ)
    new_env['LC_ALL'] = 'C'
    if simulate:
        stdout = "" if stdout is None else " > " + str(stdout)
        stdin = "" if stdin is None else " < " + str(stdin)
        print(colored("Simulation mode",'green') + ": " + colored(" ".join(cmd) + stdin + stdout, 'red'))
        return subprocess.run('true', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if type(stdout) is str:
        stdout = open(stdout, 'w')
    if type(stdin) is str:
        stdin = open(stdin, 'w')

    if shell:
        p = subprocess.run(cmd, shell=shell, env=new_env)
    else:
        p = subprocess.run(cmd, stdout=stdout, stdin=stdin, stderr=subprocess.PIPE, env=new_env)
    return p


def find_program(program):
    p = invoke('which', program, stdout=subprocess.PIPE)
    if p.returncode == 0:
        return p.stdout
    else:
        return None

