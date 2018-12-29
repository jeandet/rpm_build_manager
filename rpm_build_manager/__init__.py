#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main module."""

__author__ = "Alexis Jeandet"
__copyright__ = "Copyright 2018, Laboratory of Plasma Physics"
__credits__ = []
__license__ = "GPLv2"
__version__ = "1.0.0"
__maintainer__ = "Alexis Jeandet"
__email__ = "alexis.jeandet@member.fsf.org"
__status__ = "Development"

import os
import argparse
import glob
from termcolor import colored
from os.path import expanduser
from .common.utils import invoke
from .common.rpmbuild import make_srpm, build_with_mock, sign_rpm, update_repo, create_repo, guess_distrib_short_name
import yaml
from multiprocessing import Process

_mock_chroots_ = {}

home = expanduser("~")


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--config-file", help="config file", default=home+'/.rpm_build_manager.yml')
parser.add_argument("--list-packages", help="lists packages", action="store_true")
parser.add_argument("--sim", help="Simulation mode, just print commands", action="store_true")
args = parser.parse_args()


def list_packages():
    pass


def copy_sources(src_folder, dest_folder):
    for file in os.listdir(src_folder):
        ext = file[-5:]
        if ext != '.spec':
            invoke('cp', ['-r', src_folder + '/' + file, dest_folder])


def clone_repo(url, dest):
    invoke('git', ['clone', url, dest])


def build_package(srpm: str, chroot: str, rpmsign: bool, gpg_config: dict, destdir, additional_packages=None):
    dist, version, arch = chroot.split('-')
    short_name = guess_distrib_short_name(dist)
    repo = f'{destdir}/{version}/{arch}/'
    srpm_repo = f'{destdir}/{version}/SRPMS/'
    expected_rpm_name='.'.join(srpm.split('/')[-1].split('.')[:-3])+f'.{short_name}{version}.{arch}.rpm'
    gpg_key = str(gpg_config['key'])
    gpg_pass = str(gpg_config['pass'])
    if os.path.exists(f'''{repo}/{expected_rpm_name}'''):
        print(colored(f'[SKIP] {expected_rpm_name} already built','green'))
        return
    r = build_with_mock(srpm, chroot, additional_packages)
    rpm_list = glob.glob(f'/var/lib/mock/fedora-{version}-{arch}/result/*.{arch}.rpm')
    rpm_list += glob.glob(f'/var/lib/mock/fedora-{version}-{arch}/result/*.noarch.rpm')
    if rpmsign:
        sign_rpm(rpm_list, gpg_key, gpg_pass)
        sign_rpm(srpm, gpg_key, gpg_pass)
    if not os.path.exists(repo):
        create_repo(repo)
    for rpm in rpm_list:
        print(colored('[COPYING]', 'green'), f' {rpm} to {repo}')
        invoke('cp',[rpm, repo])
    update_repo(repo)
    if not os.path.exists(repo):
        create_repo(repo)
    invoke('cp',[srpm, srpm_repo])
    update_repo(srpm_repo)



def main():
    config = yaml.load(open(args.config_file, 'r'))
    global_config = config.pop('global')
    destdir = global_config["destdir"]
    gpg_config = {}
    if 'gpg_config' in global_config:
        gpg_config = yaml.load(open(global_config['gpg_config'], 'r'))

    if args.list_packages:
        for package in config:
            print(package)
        exit(0)

    for package in config:
        package_conf = config[package]
        clone_dir = "/tmp/rpm_buid_manager-" + package
        src_dir = clone_dir + '/' + package_conf['path']
        spec_file = clone_dir + '/' + package_conf['path'] + '/' + package_conf['spec']
        if os.path.exists(clone_dir):
            invoke('rm', ['-rf', clone_dir])
        clone_repo(package_conf['git']['url'], clone_dir)
        copy_sources(src_dir, home + '/rpmbuild/SOURCES/')
        srpm_file = make_srpm(spec_file)
        for chroot in package_conf['chroots']:
            if chroot in _mock_chroots_:
                _mock_chroots_[chroot].join()
            _mock_chroots_[chroot] = Process(target=build_package, args=(srpm_file,
                                                                         chroot,
                                                                         package_conf['rpmsign'],
                                                                         gpg_config,
                                                                         destdir,
                                                                         package_conf.get('install', None)
                                                                         )
                                             )
            _mock_chroots_[chroot].start()

    for name,process in _mock_chroots_.items():
        if process.is_alive():
            process.join()

    for dir in glob.glob('/tmp/rpm_buid_manager-*'):
        invoke('rm', ['-rf', dir])

