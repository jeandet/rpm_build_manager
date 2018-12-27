from .utils import invoke, listify


def update_repo(repo: str) -> None:
    p = invoke('createrepo', ['--update', '--deltas', repo])


def sign_packet(packet: str) -> None:
    p = invoke('rpmsign', ['--resign', packet])


def make_srpm(spec_file: str) -> str:
    p = invoke('rpmbuild', ['-bs', spec_file])
    result = p.stdout.decode()
    if 'Wrote:' in result:
        return result.split(':')[1].strip()
    return ''


def build_with_mock(srpm: str, chroot_name: str)-> object:
    return invoke('mock', ['-r', chroot_name, 'rebuild', srpm])


def sign_rpm(rpm_files: str, gpg_key: str, passphrase: str) -> None:
    rpm_files = listify(rpm_files)
    invoke('/usr/libexec/gpg-preset-passphrase', ['--passphrase', passphrase, '--preset', gpg_key])
    for rpm_file in rpm_files:
        invoke('rpmsign', ['--resign', rpm_file])
