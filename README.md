# INDIGO-specific configuration of the cloud-info-provider

The Cloud Information provider generates a representation of a site's cloud
resources, to be published inside INDIGO Configuration Management DataBase
(CMDB).

The INDIGO CMDB is a REST service storing all the information about the cloud
sites available and providing details such as the images and containers they
support. It is used as an authoritative source of information for matchmaking
and orchestration of VM and containers.

The Cloud Information Provider should be deployed at a site level and will be
used to publish information on supported images and containers at the site it
is configured for.

The generated representation is described using a
[Mako](http://www.makotemplates.org/) template having access to the cloud
middleware information.

An Ansible role is available: https://galaxy.ansible.com/indigo-dc/cloud-info-provider/

Gitbook documentation: https://indigo-dc.gitbooks.io/cloud-info-provider/content/
