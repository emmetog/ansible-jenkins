import os

import testinfra.utils.ansible_runner

from jenkins import Jenkins


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_jenkins_installed(host):
    package = host.package('jenkins')

    assert package.is_installed


def test_jenkins_user(host):
    assert host.user('jenkins').group == 'jenkins'
    assert host.user('jenkins').home == '/jenkins'


def test_jenkins_dir(host):
    assert host.file('/jenkins').is_directory
    assert host.file('/jenkins').mode == 0o0755
    assert host.file('/jenkins').user == 'jenkins'
    assert host.file('/jenkins').group == 'jenkins'
    assert host.file('/jenkins/config.xml').is_file
    assert host.file('/jenkins/config.xml').user == 'jenkins'
    assert host.file('/jenkins/config.xml').group == 'jenkins'


def test_jenkins_version():
    master = Jenkins('http://127.0.0.1:8080')
    version = master.get_version()

    assert version == '2.176.1'


def test_jenkins_plugins():
    master = Jenkins('http://127.0.0.1:8080')
    plugins = master.get_plugins()

    assert plugins['git']['active']
    assert plugins['git']['enabled']


def test_jenkins_jobs():
    master = Jenkins('http://127.0.0.1:8080')
    test_job = master.get_job_info('test_job')

    assert test_job['name'] == 'test_job'
    assert test_job['buildable']
