import os

import testinfra.utils.ansible_runner

from jenkins import Jenkins


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_jenkins_installed(host):
    package = host.package('jenkins')

    assert package.is_installed


def test_jenkins_version():
    master = Jenkins('http://127.0.0.1:8080')
    version = master.get_version()

    assert version == '2.176.1'
