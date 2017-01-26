# Administrator documentation

## Dependencies

The cloud-provider depends on PyYAML and Mako, which are already included as
dependencies for binary packages and when installing from source.

For running the cloud-provider in a production environment, depending on your
setup you will might need for OpenStack to install python-novaclient,
and python-keystoneclient.

For the INDIGO release 1, the supported OpenStack middleware is Liberty, and
the endpoint should use the v2.0 OpenStack Identity API.
v3 OpenStack Identity API is available in the mitaka_keystoneauth branch, and
will be merged to master later.

Supported OS are Ubuntu Trusty and CentOS 7.

## Binary packages

Packages are available at the [INDIGO repository](http://repo.indigo-datacloud.eu).
Use the appropriate repository for your distribution and install using the usual tools.

* ubuntu package: python-cloud-info-provider-indigo
* RHEL 7 package: cloud-info-provider-indigo

## Installing using the indigo.cloud-info-provider Ansible role

Using ansible will be the easyest way of testing, it only needs to have
Ansible 2.X available.

### Installing [indigo.cloud-info-provider Ansible role](https://galaxy.ansible.com/indigo-dc/cloud-info-provider/)

``` sh
ansible-galaxy install indigo-dc.cloud-info-provider
```

### Playbook examples

For OpenNebula middleware on an CentOS system:
``` yaml
---
- hosts: centos
  roles:
    - role: indigo-dc.cloud-info-provider
      cloud_info_provider_sitename: TEST
      cloud_info_provider_middleware: indigoon
      cloud_info_provider_setup_cron: false
      # OpenNebula configuration
      cloud_info_provider_on_auth: oneadmin:opennebula
      cloud_info_provider_on_xmlrpc_url: http://127.0.0.1:2633/RPC2
      # CMDB configuration
      cloud_info_provider_cmdb_read_url: http://indigo.cloud.plgrid.pl/cmdb
      cloud_info_provider_cmdb_write_url: http://couch.cloud.plgrid.pl/indigo-cmdb-v2
      cloud_info_provider_cmdb_user: XXXXXX
      cloud_info_provider_cmdb_password: XXXXXX
```

For OpenStack middleware on an Ubuntu system:

``` yaml
---
- hosts: ubuntu
  become: true
  roles:
    - role: indigo-dc.cloud-info-provider
      cloud_info_provider_sitename: TEST
      cloud_info_provider_middleware: openstack
      cloud_info_provider_setup_cron: false
      # OpenStack configuration
      cloud_info_provider_os_username: admin
      cloud_info_provider_os_password: openstack
      cloud_info_provider_os_auth_url: http://127.0.0.1:5000/v2.0
      cloud_info_provider_os_tenant_name: demo
      # CMDB configuration
      cloud_info_provider_cmdb_read_url: http://indigo.cloud.plgrid.pl/cmdb
      cloud_info_provider_cmdb_write_url: http://couch.cloud.plgrid.pl/indigo-cmdb-v2
      cloud_info_provider_cmdb_user: XXXXXX
      cloud_info_provider_cmdb_password: XXXXXX
```

**Test the cloud-info-provider-indigo-service output before enabling/running the cron task!**
