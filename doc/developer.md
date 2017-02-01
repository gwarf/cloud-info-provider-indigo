# Developer documentation

## Building from source

Get the source by cloning the repo and do a pip install.

As pip will have to copy files to /etc/cloud-info-provider directory,
the installation user should be able to write to it, so it is recommended to
create it before using pip.

``` sh
sudo mkdir /etc/cloud-info-provider
sudo chgrp your_user /etc/cloud-info-provider
sudo chmod g+rwx /etc/cloud-info-provider
```

### Building the cloud-info-provider python package

``` sh
git clone https://github.com/indigo-dc/cloud-info-provider
cd cloud-info-provider
pip install .
```

### Building the cloud-info-provider-indigo python package

``` sh
git clone https://github.com/indigo-dc/cloud-info-provider-indigo
cd cloud-info-provider-indigo
pip install .
```

## Building packages on Ubuntu

The build procedure is identical for the two packages.

``` sh
sudo apt update
sudo apt install -y devscripts build-essential debhelper python-all python-all-dev python-pbr python-setuptools python-support git
git clone https://github.com/indigo-dc/cloud-info-provider.git
cd cloud-info-provider
git checkout 0.7.0
debuild --no-tgz-check binary
```

``` sh
sudo apt update
sudo apt install -y devscripts build-essential debhelper python-all python-all-dev python-pbr python-setuptools python-support git
git clone https://github.com/indigo-dc/cloud-info-provider-indigo.git
cd cloud-info-provider-indigo
git checkout 0.10.0
debuild --no-tgz-check binary
```

## Building package on CentOS 7

The build dependency python-pbr comes from the OpenStack repository.

The build procedure is similar for the two packages.

### Building cloud-info-provider 0.7.0 on CentOS 7

``` sh
sudo yum clean all
sudo yum install -y centos-release-openstack-liberty
sudo yum install -y rpm-build python-pbr python-setuptools git
echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros
mkdir -p ~/rpmbuild/SOURCES
git clone https://github.com/indigo-dc/cloud-info-provider.git
cd cloud-info-provider
git checkout 0.7.0
python setup.py sdist
cp dist/cloud_info_provider-*.tar.gz ~/rpmbuild/SOURCES
rpmbuild -ba rpm/cloud-info-provider.spec
```

### Building cloud-info-provider-indigo 0.10.0 on CentOS 7

``` sh
sudo yum install -y centos-release-openstack-liberty
sudo yum install rpm-build python-pbr python-setuptools
echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros
mkdir -p ~/rpmbuild/SOURCES
git clone https://github.com/indigo-dc/cloud-info-provider-indigo.git
git checkout 0.10.0
python setup.py sdist
cp dist/cloud_info_provider_indigo-*.tar.gz ~/rpmbuild/SOURCES
rpmbuild -ba rpm/cloud-info-provider-indigo.spec
```

## Contributing to the project

Push Requests are more than welcome, the standard
[GitHub](https://guides.github.com/introduction/flow/index.html) flow will be
used.

The main steps for getting code integrated are the following:
* Fork the repository
* Work on a feature (eventually in a dedicated feature branch)
* Submit a PR (PR have to be made against the latest version of master)
* PR will be tested, discussed, validated and merged
