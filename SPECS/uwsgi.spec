Name:               uwsgi
Version:            1.0.4
Release:            2%{?dist}
Summary:            Fast, self-healing, application container server
Group:              System Environment/Daemons   
License:            GPLv2
URL:                http://projects.unbit.it/uwsgi
Source0:            http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
Source1:            rhel6.ini
Source2:            uwsgi.init
Patch0:             uwsgi_fix_rpath.patch
Patch1:             uwsgi_trick_chroot_rpmbuild.patch
BuildRequires:      curl,  python-devel, libxml2-devel, libuuid-devel
BuildRequires:      perl-ExtUtils-Embed
BuildRequires:      python-greenlet-devel
Requires(pre):      shadow-utils
Requires(post):     /sbin/service
Requires(preun):    initscripts
Requires(postun):   /sbin/service

%description
uWSGI is a fast (pure C), self-healing, developer/sysadmin-friendly
application container server.  Born as a WSGI-only server, over time it has
evolved in a complete stack for networked/clustered web applications,
implementing message/object passing, caching, RPC and process management. 
It uses the uwsgi (all lowercase, already included by default in the Nginx
and Cherokee releases) protocol for all the networking/interprocess
communications.  Can be run in preforking mode, threaded,
asynchronous/evented and supports various form of green threads/coroutine
(like uGreen and Fiber).  Sysadmin will love it as it can be configured via
command line, environment variables, xml, .ini and yaml files and via LDAP. 
Being fully modular can use tons of different technology on top of the same
core.

%package -n %{name}-devel
Summary:  uWSGI - Development header files and libraries
Group:    Development/Libraries
Requires: %{name}

%description -n %{name}-devel
This package contains the development header files and libraries
for uWSGI extensions

%package -n %{name}-plugin-common
Summary:  uWSGI - Common plugins for uWSGI
Group:    System Environment/Daemons
Requires: %{name}

%description -n %{name}-plugin-common
This package contains the most common plugins used with uWSGI. The
plugins included in this package are: cache, cgi, rpc, ugreen

%package -n %{name}-plugin-python
Summary:  uWSGI - Plugin for Python support
Group:    System Environment/Daemons
Requires: python, %{name}-plugin-common

%description -n %{name}-plugin-python
This package contains the python plugin for uWSGI

%package -n %{name}-plugin-fastrouter
Summary:  uWSGI - Plugin for FastRouter support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common

%description -n %{name}-plugin-fastrouter
This package contains the fastrouter (proxy) plugin for uWSGI

%package -n %{name}-plugin-admin
Summary:  uWSGI - Plugin for Admin support
Group:    System Environment/Daemons   
Requires: %{name}-plugin-common

%description -n %{name}-plugin-admin
This package contains the admin plugin for uWSGI

%package -n %{name}-plugin-greenlet
Summary:  uWSGI - Plugin for Python Greenlet support
Group:    System Environment/Daemons   
Requires: python-greenlet, %{name}-plugin-common

%description -n %{name}-plugin-greenlet
This package contains the python greenlet plugin for uWSGI

%prep
%setup -q
cp -p %{SOURCE1} buildconf/
echo "plugin_dir = %{_libdir}/%{name}" >> buildconf/$(basename %{SOURCE1})
%patch0 -p1
%patch1 -p1

%build
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --build rhel6.ini 

%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_includedir}/%{name}
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/run/%{name}
%{__install} -d -m 0755 %{buildroot}%{_initrddir}
%{__install} -p -m 0755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
%{__install} -p -m 0755 uwsgi %{buildroot}%{_sbindir}
%{__install} -p -m 0644 *.h %{buildroot}%{_includedir}/%{name}
%{__install} -p -m 0644 *_plugin.so %{buildroot}%{_libdir}/%{name}

%pre
getent group uwsgi >/dev/null || groupadd -r uwsgi
getent passwd uwsgi >/dev/null || \
    useradd -r -g uwsgi -d '/etc/uwsgi' -s /sbin/nologin \
    -c "uWSGI Service User" uwsgi

%post
/sbin/chkconfig --add uwsgi

%preun
if [ $1 -eq 0 ]; then
    /sbin/service uwsgi stop >/dev/null 2>&1
    /sbin/chkconfig --del uwsgi

%postun
if [ $1 -ge 1 ]; then
    /sbin/service uwsgi condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/%{name}
%{_initrddir}/%{name}
%{_sbindir}/%{name}
%attr(0755,uwsgi,uwsgi) %{_localstatedir}/log/%{name}
%attr(0755,uwsgi,uwsgi) %{_localstatedir}/run/%{name}
%doc ChangeLog LICENSE README

%files -n %{name}-devel
%{_includedir}/%{name}

%files -n %{name}-plugin-common
%{_libdir}/%{name}/cache_plugin.so
%{_libdir}/%{name}/cgi_plugin.so
%{_libdir}/%{name}/rpc_plugin.so
%{_libdir}/%{name}/ugreen_plugin.so

%files -n %{name}-plugin-python
%{_libdir}/%{name}/python_plugin.so

%files -n %{name}-plugin-fastrouter
%{_libdir}/%{name}/fastrouter_plugin.so

%files -n %{name}-plugin-admin
%{_libdir}/%{name}/admin_plugin.so

%files -n %{name}-plugin-greenlet
%{_libdir}/%{name}/greenlet_plugin.so


%changelog
* Thu Mar 08 2012 Raoul Thill <raoul.thill@gmail.com> - 1.0.4-1
- Update to 1.0.4
- Some modifications to build on RHEL6

* Mon Oct 31 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9.2-4
- Add init script to manage instances
- Add uwsgi user and group

* Fri Oct 28 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9.2-3
- Fork package from Jorge A Gallegos
- Bundle application state directories with package in preparation for init
  script bundling

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-2
- Don't download the wiki page at build time

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-1
- Updated to latest stable version
- Correctly linking plugin_dir
- Patches 1 and 2 were addressed upstream

* Sun Aug 21 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.8.3-3
- Got rid of BuildRoot
- Got rid of defattr()

* Sun Aug 14 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-2
- Added uwsgi_fix_rpath.patch
- Backported json_loads patch to work with jansson 1.x and 2.x
- Deleted clean steps since they are not needed in fedora

* Sun Jul 24 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-1
- rebuilt
- Upgraded to latest stable version 0.9.8.3
- Split packages

* Sun Jul 17 2011 Jorge Gallegos <kad@blegh.net> - 0.9.6.8-2
- Heavily modified based on Oskari's work

* Mon Feb 28 2011 Oskari Saarenmaa <os@taisia.fi> - 0.9.6.8-1
- Initial.
