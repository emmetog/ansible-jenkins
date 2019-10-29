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


def test_jenkins_secrets_files(host):
    assert host.file('/jenkins/secrets').is_directory
    assert host.file('/jenkins/secrets').mode == 0o0700
    assert host.file('/jenkins/secrets').user == 'jenkins'
    assert host.file('/jenkins/secrets').group == 'jenkins'
    test_secret_file = host.file('/jenkins/secrets/com.example.secret.xml')
    assert test_secret_file.is_file
    assert test_secret_file.user == 'jenkins'
    assert test_secret_file.group == 'jenkins'


def test_jenkins_job_files(host):
    assert host.file('/jenkins/jobs').is_directory
    assert host.file('/jenkins/jobs').user == 'jenkins'
    assert host.file('/jenkins/jobs').group == 'jenkins'
    assert host.file('/jenkins/jobs/test_job').is_directory
    assert host.file('/jenkins/jobs/test_job').user == 'jenkins'
    assert host.file('/jenkins/jobs/test_job').group == 'jenkins'
    test_job_config_file = host.file('/jenkins/jobs/test_job/config.xml')
    assert test_job_config_file.is_file
    assert test_job_config_file.user == 'jenkins'
    assert test_job_config_file.group == 'jenkins'


def test_jenkins_custom_files(host):
    assert host.file('/jenkins/userContent').is_directory
    assert host.file('/jenkins/userContent').user == 'jenkins'
    assert host.file('/jenkins/userContent').group == 'jenkins'
    assert host.file('/jenkins/userContent/index.html').is_file
    assert host.file('/jenkins/userContent/index.html').user == 'jenkins'
    assert host.file('/jenkins/userContent/index.html').group == 'jenkins'


def test_jenkins_java_process(host):
    process = host.process.get(command='/usr/bin/java')

    assert '-Djenkins.install.runSetupWizard=false' in process.args


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
