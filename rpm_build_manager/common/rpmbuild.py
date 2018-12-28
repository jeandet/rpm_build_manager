from .utils import invoke, listify
from termcolor import colored


def guess_distrib_short_name(name):
    list = {
        "fedora":"fc",
        "centos":"el",
        "epel":"el"
    }

    return list.get(name, "")


def update_repo(repo: str) -> None:
    print(colored('[UPDATEREPO]', 'green'), f' {repo}')
    p = invoke('createrepo', ['--update', '--deltas', repo])


def create_repo(repo: str) -> None:
    print(colored('[CRATEREPO]', 'green'), f' {repo}')
    invoke('mkdir', ['-p', repo])
    p = invoke('createrepo', [repo])


def make_srpm(spec_file: str) -> str:
    p = invoke('rpmbuild', ['-bs', spec_file])
    result = p.stdout.decode()
    if 'Wrote:' in result:
        return result.split(':')[1].strip()
    return ''


def build_with_mock(srpm: str, chroot_name: str)-> object:
    print(colored('[MOCKBUILD]', 'green'), f' {srpm} for {chroot_name}')
    return invoke('mock', ['-r', chroot_name, 'rebuild', srpm])


def sign_rpm(rpm_files: str, gpg_key: str, passphrase: str) -> None:
    rpm_files = listify(rpm_files)
    for rpm_file in rpm_files:
        print(colored('[SIGNING]', 'green'), f' {rpm_file}')
        invoke('rpm-sign', [passphrase, rpm_file])
