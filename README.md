Ansible Role for Jenkins
========================

Installs and completely configures Jenkins using Ansible.

This role is used when you want all your Jenkins configuration
in version control so you can deploy Jenkins repeatably
and reliably and you can treat your Jenkins as a [Cow instead
of a Pet](https://blog.engineyard.com/2014/pets-vs-cattle).

If you are looking for a role to install Jenkins and you
want to configure everything through the web interface and you
don't care about being able to repeatably deploy this
same fully-configured Jenkins then you don't need
this role, have a look at the
[geerlingguy/ansible-role-jenkins](https://github.com/geerlingguy/ansible-role-jenkins)
role instead.

Requirements
------------

Requires curl to be installed on the server.

If deploying using Docker then you need Docker
installed on the server.

(Docker, apt-get and yum are the only supported ways at the moment
although more ways can easily be added, PRs welcome).

Installation
------------

Install using ansible galaxy:

```
$ ansible-galaxy install emmetog.jenkins
```

Role Variables
--------------

```yml
jenkins_version: "2.73.1" # The exact version of jenkins to deploy

jenkins_url: "http://127.0.0.1" # The url that Jenkins will be accessible on
jenkins_port: "8080" # The port that Jenkins will listen on
jenkins_home: /data/jenkins # The directory on the server where the Jenkins configs will live
jenkins_admin: "admin@example.com" # The admininstrator email address for the Jenkins server

# If you need to override any java options then do that here.
jenkins_java_opts: "-Djenkins.install.runSetupWizard=false"

# Install Jenkins by means of a Docker container
jenkins_install_via: "docker"

# Install Jenkins directly on Ubuntu/Debian Linux systems
jenkins_install_via: "apt"

# Install Jenkins directly on RedHat/CentOS Linux systems
jenkins_install_via: "yum"

# Configuration files owner and group
jenkins_config_owner: "ubuntu"
jenkins_config_group: "ubuntu"

# The locations of the configuration files for jenkins
jenkins_source_dir_configs: "{{ playbook_dir }}/jenkins-configs"
jenkins_source_dir_jobs: "{{ jenkins_source_dir_configs }}/jobs"

# config.xml template source
jenkins_source_config_xml: "{{ jenkins_source_dir_configs }}/config.xml"

# Include custom files for jenkins installation
jenkins_include_custom_files: false
jenkins_custom_files: {}

# Include secrets directory during installation
jenkins_include_secrets: false
jenkins_source_secrets: "{{ jenkins_source_dir_configs }}/secrets/"

# The names of the jobs (config.xml must exist under jenkins_source_dir_jobs/job_name/)
jenkins_jobs: []

# These plugins will be installed in the jenkins instance
jenkins_plugins:
  - git
  - log-parser
  - copyartifact
  - workflow-aggregator
  - workflow-multibranch
  - docker-workflow
  - template-project
  - ec2

# List of sources of custom jenkins plugins to install
jenkins_custom_plugins: []

###################################################
# Docker vars: apply to deploying via docker only #
###################################################

# The docker hub image name
jenkins_docker_image: "jenkins/jenkins"

# Configs specific to the "docker" method of running jenkins
# The name of the jenkins container
jenkins_docker_container_name: jenkins

# Default, if true, the port will be exposed on the host (using "port")
# If set to false, the port will only be exposed to other containers (using "expose")
jenkins_docker_expose_port: true


#############################################
# Apt vars: apply to deploying via apt only #
#############################################

# Packages which are to be installed on the jenkins instance
jenkins_apt_packages:
  - openjdk-8-jdk

# Java version to use. Note that JDK 8 is required for Jenkins
# 2.54 or greater.
jenkins_java_version: "java-1.8.0-openjdk-amd64"

```

Example Playbook
----------------

```yml
- hosts: jenkins

  vars:
    jenkins_version: "2.73.1"
    jenkins_url: http://jenkins.example.com
    jenkins_port: 80
    jenkins_install_via: "docker"
    jenkins_jobs:
        - "my-first-job"
        - "another-awesome-job"
    jenkins_include_secrets: true
    jenkins_include_custom_files: true
    jenkins_custom_files:
      - src: "jenkins.plugins.openstack.compute.UserDataConfig.xml"
        dest: "jenkins.plugins.openstack.compute.UserDataConfig.xml"
    jenkins_custom_plugins:
        - "openstack-cloud-plugin/openstack-cloud.jpi"

  roles:
    - emmetog.jenkins
```

HTTPS
-----

If you want to enable HTTPS on jenkins we recommend that you use a
reverse proxy like [jwilder/nginx-proxy](https://github.com/jwilder/nginx-proxy)
or [traefik](https://github.com/containous/traefik) and configure it
as the HTTPS endpoint instead of configuring jenkins itself with HTTPS.
This gives you more flexibility and better separation of concerns. See
the documentation in those projects for more details on how to deploy
the proxies and configure HTTPS.

If using a reverse proxy in front of the jenkins
instance and deploying using docker you probably
want to set the `jenkins_docker_expose_port` var to false so that the
port is not exposed on the host, only to the reverse proxy.

Authentication and Security
---------------------------

This role supports the following authentication mechanisms for Jenkins:

1. API token-based authentication (recommended, requires at least Jenkins 2.96)
2. Crumb-based authentication with the [Strict Crumb Issuer
   plugin](https://plugins.jenkins.io/strict-crumb-issuer) (required if _not_
   using API tokens and Jenkins 2.176.2 or newer)
3. No security (not recommended)

*API token-based authentication*

API token-based authentication is recommended, but requires a bit of extra
effort to configure. The advantage of API tokens is that they can be easily
revoked in Jenkins, and their usage is also tracked. API tokens also do not
require getting a crumb token, which has become more difficult since Jenkins
version 2.172.2 (see [this security
bulletin](https://jenkins.io/security/advisory/2019-07-17/#SECURITY-626).

To create an API token, you'll need to do the following:

1. All API tokens must belong to a specific user. So either create a special
   user for deployments, or log in as the administrator or another account.
2. In the user's configuration page, click the "Add new Token" button.
3. Save the token value, preferably in an Ansible vault.
4. Define the following variables in your playbook:
  - `jenkins_auth: "api"`
  - `jenkins_api_token: "(defined in the Anible vault)"`
  - `jenkins_api_username: "(defined in the Ansible vault)"`
5. Create a backup of the file `$JENKINS_HOME/users/the_username/config.xml`,
   where `the_username` corresponds to the user which owns the API token you
   just created.
6. Add this file to your control host, and make sure that is deployed to Jenkins
   in the `jenkins_custom_files` list, like so:

```
jenkins_custom_files:
  - src: "users/the_username/config.xml"
    dest: "users/ci/config.xml"
```

Note that you may need to change the `src` value, depending on where you save
the file on the control machine relative to the playbook.

*Crumb-based authentication*

Crumb-based authentication can be used to prevent cross-site request forgery
attacks and is recommended if API tokens are impractical. However, it can also
be a bit tricky to configure this due to security fixes in Jenkins. To configure
CSRF, you'll need to do the following:

1. If you are using Jenkins >= 2.176.2, you'll need to install the
   Strict Crumb Issuer plugin. This can be done by this role by adding the
   `strict-crumb-issuer` ID to the `jenkins_plugins` list.
2. In Jenkins, click on "Manage Jenkins" -> "Configure Global Security"
3. In the "CSRF Protection" section, enable "Prevent Cross Site Request Forgery
   exploits", and then select "Strict Crumb Issuer" if using Jenkins >= 2.176.2,
   or otherwise "Default Crumb Issuer". Note that to see this option, you'll
   need to have the Strict Crumb Issuer plugin installed.  Afterwards, you'll
   also need to backup the main Jenkins `config.xml` file to the control host.

Likewise, for the above to work, you'll need at least Ansible 2.9.0pre5 or 2.10
(which are, at the time of this writing, both in development. See [this Ansible
issue](https://github.com/ansible/ansible/issues/61672) for more details).

Jenkins Configs
---------------

The example above will look for the job configs in
`{{ playbook_dir }}/jenkins-configs/jobs/my-first-job/config.xml` and
`{{ playbook_dir }}/jenkins-configs/jobs/another-awesome-job/config.xml`.

***NOTE***: These directories are customizable, see the `jenkins_source_dir_configs` and `jenkins_source_dir_jobs` role variables.

The role will also look for `{{ playbook_dir }}/jenkins-configs/config.xml`
These config.xml will be templated over to the server to be used as the job configuration.
It will upload the whole secrets directory under `{{ playbook_dir }}/jenkins-configs/secrets` and configure custom files provided under `{{ jenkins_custom_files }}` variable. Note that `{{ jenkins_include_secrets }}` and `{{ jenkins_include_custom_files }}` variables should be set to true for these to work.
Additionally the role can install custom plugins by providing the .jpi or .hpi files as a list under `{{ jenkins_custom_plugins }}` variable.

config.xml and custom files are templated so you can put variables in them,
for example it would be a good idea to encrypt sensitive variables
in ansible vault.

Example Job Configs
-------------------

Here's an example of what you could put in `{{ playbook_dir }}/jenkins-configs/jobs/my-first-job/config.xml`:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description>My first job, it says "hello world"</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>echo &quot;Hello World!&quot;</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>
```

Example Jenkins Configs
-----------------------

In `{{ jenkins_source_dir_configs }}/config.xml` you put your global
Jenkins configuration, for example:
```xml
<?xml version='1.0' encoding='UTF-8'?>
<hudson>
    <disabledAdministrativeMonitors/>
    <version></version>
    <numExecutors>2</numExecutors>
    <mode>NORMAL</mode>
    <useSecurity>true</useSecurity>
    <authorizationStrategy class="hudson.security.AuthorizationStrategy$Unsecured"/>
    <securityRealm class="hudson.security.SecurityRealm$None"/>
    <disableRememberMe>false</disableRememberMe>
    <projectNamingStrategy class="jenkins.model.ProjectNamingStrategy$DefaultProjectNamingStrategy"/>
    <workspaceDir>${ITEM_ROOTDIR}/workspace</workspaceDir>
    <buildsDir>${ITEM_ROOTDIR}/builds</buildsDir>
    <jdks/>
    <viewsTabBar class="hudson.views.DefaultViewsTabBar"/>
    <myViewsTabBar class="hudson.views.DefaultMyViewsTabBar"/>
    <clouds>
        <hudson.plugins.ec2.EC2Cloud plugin="ec2@1.33">
            <name>ec2-slave-docker-ec2</name>
            <useInstanceProfileForCredentials>false</useInstanceProfileForCredentials>
            <credentialsId>jenkins-aws-ec2</credentialsId>

            <privateKey class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
                <privateKey>{{ ssh_jenkins_aws_key }}</privateKey>
            </privateKey>

            <instanceCap>1</instanceCap>
            <templates>
                <hudson.plugins.ec2.SlaveTemplate>
                    <ami>ami-2654d755</ami>
                    <description>Docker builder</description>
                    <zone>eu-west-1c</zone>
                    <securityGroups>ssh-only</securityGroups>
                    <remoteFS></remoteFS>
                    <type>T2Micro</type>
                    <ebsOptimized>false</ebsOptimized>
                    <labels>docker</labels>
                    <mode>NORMAL</mode>
                    <initScript></initScript>
                    <tmpDir></tmpDir>
                    <userData></userData>
                    <numExecutors>1</numExecutors>
                    <remoteAdmin>ubuntu</remoteAdmin>
                    <jvmopts></jvmopts>
                    <subnetId></subnetId>
                    <idleTerminationMinutes>30</idleTerminationMinutes>
                    <iamInstanceProfile></iamInstanceProfile>
                    <useEphemeralDevices>false</useEphemeralDevices>
                    <customDeviceMapping></customDeviceMapping>
                    <instanceCap>2147483647</instanceCap>
                    <stopOnTerminate>true</stopOnTerminate>
                    <usePrivateDnsName>false</usePrivateDnsName>
                    <associatePublicIp>false</associatePublicIp>
                    <useDedicatedTenancy>false</useDedicatedTenancy>
                    <amiType class="hudson.plugins.ec2.UnixData">
                        <rootCommandPrefix></rootCommandPrefix>
                        <sshPort>22</sshPort>
                    </amiType>
                    <launchTimeout>2147483647</launchTimeout>
                    <connectBySSHProcess>false</connectBySSHProcess>
                    <connectUsingPublicIp>false</connectUsingPublicIp>
                </hudson.plugins.ec2.SlaveTemplate>
            </templates>
            <region>eu-west-1</region>
        </hudson.plugins.ec2.EC2Cloud>
    </clouds>
    <quietPeriod>5</quietPeriod>
    <scmCheckoutRetryCount>0</scmCheckoutRetryCount>
    <views>
        <hudson.model.AllView>
            <owner class="hudson" reference="../../.."/>
            <name>All</name>
            <filterExecutors>false</filterExecutors>
            <filterQueue>false</filterQueue>
            <properties class="hudson.model.View$PropertyList"/>
        </hudson.model.AllView>
    </views>
    <primaryView>All</primaryView>
    <slaveAgentPort>50000</slaveAgentPort>
    <label></label>
    <nodeProperties/>
    <globalNodeProperties/>
</hudson>
```

Making Changes
--------------

When you want to make a big change in a configuration file
or you want to add a new job the normal workflow is to make
the change in the Jenkins UI
first, then copy the resulting XML back into your VCS.

License
-------

MIT

Author Information
------------------

Made with love by Emmet O'Grady.

I am the founder of [NimbleCI](https://nimbleci.com) which
builds Docker containers for feature branch workflow projects in Github.

I blog on my [personal blog](http://blog.emmetogrady.com) and
about Docker related things on the [NimbleCI blog](https://blog.nimbleci.com).
