#
# cloud-info-provider-indigo RPM
#

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary: INDIGO configuration for Information provider for Cloud Compute and Cloud Storage services
Name: cloud-info-provider-indigo
Version: 0.10.0
Release: 1%{?dist}
Group: Applications/Internet
License: ASL 2.0
URL: https://github.com/indigo-dc/cloud-info-provider-indigo
Source: cloud_info_provider_indigo-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python-setuptools
BuildRequires: python-pbr
Requires: python
Requires: python-argparse
Requires: python-requests
Requires: cloud-info-provider
BuildArch: noarch

%description
INDIGO-specific configuration for Information provider for Cloud Compute and Cloud Storage services.
Using the provided templates, the cloud-info-provider can output JSON formatted information.
A script allowing to send data to INDIGO CMDB is also provided.

%prep
%setup -q -n cloud_info_provider_indigo-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{python_sitelib}/cloud_info*
/usr/bin/send-to-cmdb
%config /etc/cloud-info-provider/templates

%changelog
* Mon Jan 23 2017 Baptiste Grenier <baptiste.grenier@egi.eu> - 0.10.0-{%release}
- First release after removing all non INDIGO-specific files from this package.
