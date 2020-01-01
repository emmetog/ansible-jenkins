Ansible Role for Jenkins
========================

Installs and completely configures Jenkins using Ansible.

This role is used when you want all your Jenkins configuration in version
control so you can deploy Jenkins repeatably and reliably and you can treat your
Jenkins as a [Cow instead of a
Pet](https://blog.engineyard.com/2014/pets-vs-cattle).

If you are looking for a role to install Jenkins and you want to configure
everything through the web interface and you don't care about being able to
repeatably deploy this same fully-configured Jenkins, then you don't need this
role. Instead, have a look at the
[geerlingguy/ansible-role-jenkins](https://github.com/geerlingguy/ansible-role-jenkins)
role instead.

Requirements
------------

If deploying using Docker, then you need Docker installed on the server. Docker,
apt-get, and yum are the only supported ways at the moment although more ways
can easily be added, PRs welcome.

Installation
------------

Install using Ansible Galaxy:

```
$ ansible-galaxy install emmetog.jenkins
```

Role Variables
--------------

The following variables influence how Jenkins is installed:

- `jenkins_install_via`: Controls how Jenkins is installed. **Important**: This
  variable must be defined to one of the following values:
  - `docker`: Install in a Docker container
  - `apt`: Install Jenkins directly on Ubuntu/Debian Linux systems
  - `yum`: Install Jenkins directly on RedHat/CentOS Linux systems
- `jenkins_version`: The exact version of Jenkins to install

The following variables influence how Jenkins is configured:

- `jenkins_url`: The URL that Jenkins will be accessible on
- `jenkins_port`: The port that Jenkins will listen on
- `jenkins_home`: The directory on the server where the Jenkins configs will
  live
- `jenkins_admin`: The administrator's email address for the Jenkins server
- `jenkins_java_opts`: Options passed to the Java executable
- `jenkins_config_owner`: Owner of Jenkins configuration files
- `jenkins_config_group`: Group of Jenkins configuration files
- `jenkins_auth`: How Ansible should authenticate itself with Jenkins, (see the
  "Authentication and Security" section below)
- `jenkins_url_health_check`: which url to use for the health check after jenkins is started (defaults to `jenkins_url`)
- `jenkins_health_check_user`: if defined, uses basic auth (see API token section) for health check with this username (useful if you set up e.g. Google OAuth)
- `jenkins_health_check_password`: if defined, uses basic auth (see API token section) for health check with this password (useful if you set up e.g. Google OAuth)

The following list variables influence the jobs/plugins that will be installed
in Jenkins:

- `jenkins_jobs`: List of names of the jobs to copy to Jenkins. The `config.xml`
  file must exist under `jenkins_source_dir_jobs/<job_name>`
- `jenkins_plugins`: List of plugin IDs to install on Jenkins.
- `jenkins_custom_plugins`: List of custom plugins to install on Jenkins.

For a complete list of variables, see [`defaults/main.yml`](defaults/main.yml).

Example Playbook
----------------

```yml
- hosts: jenkins

  vars:
    jenkins_version: "2.73.1"
    jenkins_hostname: "jenkins.example.com"
    jenkins_port: 8080
    jenkins_install_via: "docker"
    jenkins_jobs:
      - "my-first-job"
      - "another-awesome-job"
    jenkins_include_secrets: true
    jenkins_include_custom_files: true
    jenkins_custom_files:
      - src: "jenkins.plugins.openstack.compute.UserDataConfig.xml"
        dest: "jenkins.plugins.openstack.compute.UserDataConfig.xml"
    jenkins_plugins:
      - git
      - blueocean
    jenkins_custom_plugins:
      - "openstack-cloud-plugin/openstack-cloud.jpi"

  roles:
    - emmetog.jenkins
```

Managing Configuration Files
----------------------------

The example above will look for job configuration files in
`{{ playbook_dir }}/jenkins-configs/jobs/my-first-job/config.xml` and
`{{ playbook_dir }}/jenkins-configs/jobs/another-awesome-job/config.xml`.

**NOTE**: These directories are customizable, see the
`jenkins_source_dir_configs` and `jenkins_source_dir_jobs` role variables.

The role will also look for `{{ playbook_dir }}/jenkins-configs/config.xml`
This `config.xml` file will be copied to the server and used as the job
configuration template.

The above example will also upload the entire secrets directory under
`{{ playbook_dir }}/jenkins-configs/secrets`, and also copy custom files
defined in the `{{ jenkins_custom_files }}` variable. Note that
`{{ jenkins_include_secrets }}` and `{{ jenkins_include_custom_files }}`
variables should be set to `true` for features these to work. Additionally,
the role can install custom plugins by providing the .jpi or .hpi files in the
`{{ jenkins_custom_plugins }}` list variable.

The `config.xml` and the custom files are treated as templates so you can put
variables in them, including sensitive data from the Ansible vault.

When you want to make a change in a configuration file, or you want to add a
new item (such as a job, plugin, etc) the normal workflow is:

1. Make the change in the Jenkins UI
2. Copy the resulting XML files back into your VCS
3. For newly-created files, don't forget to add them to the respective list:
  - For new jobs, these must be added to `jenkins_jobs`
  - For custom files, these must be added to `jenkins_include_custom_files`
  - For custom plugins, these must be added to `jenkins_custom_plugins`

Example Jenkins Configuration File
----------------------------------

In `{{ jenkins_source_dir_configs }}/config.xml` you put your global Jenkins
configuration, for example:

```xml
<?xml version='1.1' encoding='UTF-8'?>
<hudson>
  <disabledAdministrativeMonitors/>
  <version>2.176.1</version>
  <installStateName>RESTART</installStateName>
  <numExecutors>1</numExecutors>
  <mode>EXCLUSIVE</mode>
  <useSecurity>true</useSecurity>
  <authorizationStrategy class="hudson.security.AuthorizationStrategy$Unsecured"/>
  <securityRealm class="hudson.security.HudsonPrivateSecurityRealm">
    <disableSignup>false</disableSignup>
    <enableCaptcha>false</enableCaptcha>
  </securityRealm>
  <disableRememberMe>false</disableRememberMe>
  <projectNamingStrategy class="jenkins.model.ProjectNamingStrategy$DefaultProjectNamingStrategy"/>
  <workspaceDir>${JENKINS_HOME}/workspace/${ITEM_FULLNAME}</workspaceDir>
  <buildsDir>${ITEM_ROOTDIR}/builds</buildsDir>
  <markupFormatter class="hudson.markup.EscapedMarkupFormatter"/>
  <jdks/>
  <viewsTabBar class="hudson.views.DefaultViewsTabBar"/>
  <myViewsTabBar class="hudson.views.DefaultMyViewsTabBar"/>
  <clouds/>
  <quietPeriod>0</quietPeriod>
  <scmCheckoutRetryCount>0</scmCheckoutRetryCount>
  <views>
    <hudson.model.AllView>
      <owner class="hudson" reference="../../.."/>
      <name>all</name>
      <filterExecutors>false</filterExecutors>
      <filterQueue>false</filterQueue>
      <properties class="hudson.model.View$PropertyList"/>
    </hudson.model.AllView>
  </views>
  <primaryView>all</primaryView>
  <slaveAgentPort>0</slaveAgentPort>
  <disabledAgentProtocols>
    <string>JNLP-connect</string>
    <string>JNLP2-connect</string>
  </disabledAgentProtocols>
  <label>master</label>
  <crumbIssuer class="hudson.security.csrf.DefaultCrumbIssuer">
    <excludeClientIPFromCrumb>false</excludeClientIPFromCrumb>
  </crumbIssuer>
  <nodeProperties/>
  <globalNodeProperties/>
</hudson>
```

Example Job Configuration File
------------------------------

Here's an example of what you could put in
`{{ playbook_dir }}/jenkins-configs/jobs/my-first-job/config.xml`:

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
    dest: "users/the_username/config.xml"
```

Note that you may need to change the `src` value, depending on where you save
the file on the control machine relative to the playbook.

*Crumb-based authentication*

Crumb-based authentication can be used to prevent cross-site request forgery
attacks and is recommended if API tokens are impractical. **Note**: crumb-based
authentication only works with the "Anyone can do anything" access control
setting. If your Jenkins configuration requires a stricter security setup, you
should use API tokens (documented above).

Crumb-based authentication can also be a bit tricky to configure due to recent
security fixes in Jenkins. To configure CSRF, you'll need to do the following:

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

HTTPS
-----

If you want to enable HTTPS on Jenkins, this can be done as follows:

- Define `jenkins_port_https` to the port that Jenkins should listen on
- Define variables *either* for the JKS keystore or the CA signed certificate:
  * For JKS keystore, you'll need to define:
    - `jenkins_https_keystore`: Path to the keystore file on the control host,
      which will be copied to the Jenkins server by this role.
    - `jenkins_https_keystore_password`: Password for said JKS keystore. Use of
      the Ansible vault is recommended for this. **IMPORTANT**: This string
      will be written in plaintext to the Jenkins configuration file on the
      server. It will also be visible in the server's process list. Consider
      migrating your certificate to a signed certificate file (see below).
  * For a CA signed certificate file, you'll need to define:
    - `jenkins_https_certificate`: Path to the certificate file, which will be
      copied to the Jenkins server by this role. Use of the Ansible vault is
      recommended for this file.
    - `jenkins_https_private_key`: Private key for said CA signed certificate.
      Use of the Ansible vault is recommended for this file.
- Optionally, `jenkins_https_validate_certs` should be defined to `false` if
  you are using a self-signed certificate.

If you are deploying Jenkins with Docker, then using a reverse proxy such as
[jwilder/nginx-proxy](https://github.com/jwilder/nginx-proxy) or
[traefik](https://github.com/containous/traefik) is recommended instead of
configuring Jenkins itself. This gives a bit more flexibility and allows for
separation of responsibilities. See the documentation in those projects for
more details on how to deploy the proxies and configure HTTPS.

If using a reverse proxy in front of the Jenkins instance and deploying using
Docker you probably want to set the `jenkins_docker_expose_port` variable to
false so that the port is not exposed on the host, only to the reverse proxy.

License
-------

MIT

Author Information
------------------

Made with love by Emmet O'Grady.

I am the founder of [NimbleCI](https://nimbleci.com) which builds Docker
containers for feature branch workflow projects in Github.

I blog on my [personal blog](http://blog.emmetogrady.com) and about Docker
related things on the [NimbleCI blog](https://blog.nimbleci.com).
