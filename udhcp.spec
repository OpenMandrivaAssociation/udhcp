# OE: conditional switches
#
#(ie. use with rpm --rebuild):
#
#	--with diet	Compile udhcp against dietlibc

%bcond_with	diet
%bcond_without	uclibc
%define snapshot 20050303

Summary:	Very small DHCP server/client
Name:		udhcp
Version:	0.9.9
Release:	0.%{snapshot}.5
License:	GPLv2+
Group:		System/Servers
URL:		https://udhcp.busybox.net/
Source0:	http://udhcp.busybox.net/source/%{name}-%{snapshot}.tar.gz
Source1:	udhcpd.conf
Source2:	udhcpd.init
Patch0:		udhcp-0.9.9-build-options.patch
Patch1:		udhcp-0.9.9-change-client-installation-prefix.patch
# http://www.lart.info/~bwachter/projects/dietlinux/download/current/patches/udhcp-0.9.8-dietlibc.patch
# P1 is rediffed for system dietlibc (only Makefile.dietlibc)
Patch2:		udhcp-0.9.8-dietlibc.patch
Patch3:		udhcp-0.9.9-fwhole-program.patch
Patch4:		udhcp-0.9.9-etc-resolv.conf-path.patch
%if %{with diet}
BuildRequires:	dietlibc-devel >= 0.20-1mdk
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel
%endif

%description 
This is the very small DHCP server and client written by Moreton Bay/Lineo.

%package -n	udhcpd
Summary:	Very small DHCP server
Group:		System/Servers
Requires(preun):rpm-helper
Requires(post):	rpm-helper

%description -n	udhcpd
This is the very small DHCP server written by Moreton Bay/Lineo.

%package -n	udhcpc
Summary:	Very small DHCP client
Group:		System/Configuration/Networking

%description -n	udhcpc
This is the very small DHCP client written by Moreton Bay/Lineo.

%package -n	uclibc-udhcp
Summary:	Verry small DHCP client & server (uClibc build)
Group:		System/Configuration/Networking
Requires:	udhcpd = %{EVRD} udhcpc = %{EVRD}

%description -n	uclibc-udhcp
This is the very small DHCP client & server written by Moreton Bay/Lineo.

%prep
%setup -q -n %{name}
%patch0 -p1 -b .options~
%patch1 -p1 -b .install~

%if %{with diet}
%patch2 -p1 -b .DIET~
%ifarch x86_64
sed -e "s|lib-i386|lib-x86_64|g" -i Makefile.dietlibc
%endif
%endif
%patch3 -p1 -b .fwhole_program~
%patch4 -p1 -b .etcresolv~

%if %{with uclibc}
mkdir .uclibc
cp -a * .uclibc
%endif

%build
%serverbuild

%if %{with diet}
%make -f Makefile.dietlibc STRIP=/bin/true
%else
%make STRIP=/bin/true
%endif

%if %{with uclibc}
pushd .uclibc
 CC="%{uclibc_cc}" LD="%{uclibc_cc}" CFLAGS="%{uclibc_cflags}" %make COMBINED_BINARY=1 STRIP=/bin/true
%endif

%install
%makeinstall_std STRIP=/bin/true

%if %{with uclibc}
%makeinstall_std SBINDIR=%{buildroot}%{uclibc_root}/sbin USRSBINDIR=%{buildroot}%{uclibc_root}%{_sbindir} USRBINDIR=%{buildroot}%{uclibc_root}%{_bindir}
%endif

install -m0644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/udhcpd.conf
install -m0755 %{SOURCE2} -D %{buildroot}%{_initrddir}/udhcpd

install -d %{buildroot}%{_localstatedir}/lib/udhcpd
touch %{buildroot}%{_localstatedir}/lib/udhcpd/udhcpd.leases

%post -n udhcpd
%_post_service udhcpd
# New udhcpd lease file
if [ ! -f %{_localstatedir}/lib/udhcpd/udhcpd.leases ]; then
    touch %{_localstatedir}/lib/udhcpd/udhcpd.leases
fi

%preun -n udhcpd
%_preun_service udhcpd

%files -n udhcpd
%doc README COPYING AUTHORS TODO samples/udhcpd.conf
%config(noreplace) %{_sysconfdir}/udhcpd.conf
%{_initrddir}/udhcpd
%dir %{_localstatedir}/lib/udhcpd/
%config(noreplace) %ghost %{_localstatedir}/lib/udhcpd/udhcpd.leases
%{_sbindir}/udhcpd
%{_bindir}/dumpleases
%{_mandir}/man1/dumpleases.*
%{_mandir}/man5/udhcpd.conf.*
%{_mandir}/man8/udhcpd.*

%files -n udhcpc
%doc README COPYING AUTHORS TODO samples/sample*
/sbin/udhcpc
%dir %{_sysconfdir}/udhcpc
%config(noreplace) %{_sysconfdir}/udhcpc/default.bound
%config(noreplace) %{_sysconfdir}/udhcpc/default.deconfig 
%config(noreplace) %{_sysconfdir}/udhcpc/default.nak    
%config(noreplace) %{_sysconfdir}/udhcpc/default.renew
%config(noreplace) %{_sysconfdir}/udhcpc/default.script    

%{_mandir}/man8/udhcpc.*

%if %{with uclibc}
%files -n uclibc-udhcp
%{uclibc_root}/sbin/udhcpc
%{uclibc_root}%{_bindir}/dumpleases
%{uclibc_root}%{_sbindir}/udhcpd
%endif
