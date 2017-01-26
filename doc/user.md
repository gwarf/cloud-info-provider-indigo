# User documentation

## Using the provider and configuring its output

Depending on the template used output can range from JSON to LDIF.

The ```--template-extension``` (default: ```indigo```) allows to select different
templates based on thier file extension.
Templates should be available inside the directory ```--template-dir```
(default: ```/etc/cloud-info-provider-indigo/templates```)

The ```--yaml-file``` (default ```/etc/cloud-info-provider-indigo/static.yaml``` allows
to set some static values (see sample.static.yaml for a complete example with comments).

Simple example of ```/etc/cloud-info-provider-indigo/static.yaml``` for an opennebula
endpoint:

For OpenNebula the endpoints section is required, but for OpenStack it can be
omitted.
For other templates (ie ldif) some more information might need to be added to
the `static.yaml` file, see the examples available inside the
`/etc/cloud-info-provider-indigo` directory.

``` yaml
site:
    name: TEST

compute:
    endpoints:
        https://localhost:2633/RPC2:
    images:
        defaults:
            # Set to False or comment the line below if you want to show
            # all the images installed in the site (also snapshots). Otherwise
            # only images with a valid marketplace ID (set by the marketplace
            # custom property) are shown
            require_marketplace_id: false
```

Dynamic information can be further obtained with the middleware providers
(OpenStack and OpenNebula supported currently). Use the
`--middleware` option for specifying the provider to use (see the command
help for exact names). cloud-info-provider will fallback to static information
defined in the yaml file if a dynamic provider is not able to return any
information. See the `sample.openstack.yaml` and `sample.opennebula.yaml`
for example configurations for each provider.

Each dynamic provider has its own commandline options for specifying how
to connect to the underlying service. Use the `--help` option for a complete
listing of options.

For example for OpenStack, use a command line similar to the following:
```
cloud-info-provider-indigo-service \
  --middleware openstack \
  --os-username <username> \
  --os-password <password> \
  --os-tenant-name <tenant> \
  --os-auth-url <auth-url>
```
The auth-url should be something like this: ` http://192.168.56.101:5000/v2.0 `.

For example for OpenNebula, use a command line similar to the following:
```
cloud-info-provider-indigo-service \
  --middleware indigoon \
  --on-auth <username>:<password> \
  --on-rpcxml-endpoint <rpc-xml-endpoint>
```
The rpc-xml-endpoint should be something like this: ` http://localhost:2633/RPC2 `.

## Running the provider in a cloud resource middleware

This is the normal deployment mode for the cloud provider. It should be installed
in a node with access to your cloud infrastructure: for OpenStack, access to
nova service is needed; for OpenNebula access to the XML endpoint is required.

## Importing cloud middleware information inside an INDIGO CMDB.

The provided ```send-to-cmdb``` python script allows to interact with the CMDB.
It will expect JON from its standard input and use CMDB API to import/update
information about images available in the cloud middleware.

``` sh
cloud-info-provider-indigo-service \
  --middleware openstack \
  --os-username <username> \
  --os-password <password> \
  --os-tenant-name <tenant> \
  --os-auth-url <auth-url> \
  | send-to-cmdb \
  --cmdb-user <cmdb-user> \
  --cmdb-password <cmdb-password> \
  --sitename <sitename>
```

Real example

``` sh
cloud-info-provider-indigo-service \
  --middleware openstack \
  --os-username admin \
  --os-tenant-name demo \
  --os-password openstack \
  --os-auth-url http://192.168.56.101:5000/v2.0 \
  | send-to-cmdb \
  --cmdb-user cmdb_user \
  --cmdb-password cmdb_password \
  --sitename CYFRONET-CLOUD \
  --delete-non-local-images \
  -v
```

Use ```send-to-cmdb --help``` to see the list of available options
(```--cmdb-read-endpoint``` and ```--cmdb-write-endpoint``` allowing to specify
CMDB endpoints).

The ` --delete-non-local-images ` send-to-cmdb parameter will delete images in
the CMDB that are not present in the configured cloud, when testing it,
checking the vervbose `-v` output might be useful.

**Test the generation of the output before importing the provider output to the CMDB!**

If needed it is possible to run the cloud information provider on a regular
basis using a cron task.
