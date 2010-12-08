# OE: conditional switches
#
#(ie. use with rpm --rebuild):
#
#	--with diet	Compile udhcp against dietlibc

%define build_diet 0
%define snapshot 20050303

# commandline overrides:
# rpm -ba|--rebuild --with 'xxx'
%{?_with_diet: %{expand: %%define build_diet 1}}


Summary:	Very small DHCP server/client
Name:		udhcp
Version:	0.9.9
Release:	%mkrel 0.%{snapshot}.2
License:	GPL
Group:		System/Servers
URL:		http://udhcp.busybox.net/
Source0:	http://udhcp.busybox.net/source/%{name}-%{snapshot}.tar.gz
Source1:	udhcpd.conf
Source2:	udhcpd.init
Patch0:		udhcp-0.9.9-build-options.patch
Patch1:		udhcp-0.9.9-change-client-installation-prefix.patch
# http://www.lart.info/~bwachter/projects/dietlinux/download/current/patches/udhcp-0.9.8-dietlibc.patch
# P1 is rediffed for system dietlibc (only Makefile.dietlibc)
Patch2:		udhcp-0.9.8-dietlibc.patch
%if %{build_diet}
BuildRequires:	dietlibc-devel >= 0.20-1mdk
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%prep
%setup -q -n %{name}
%patch0 -p1 -b .options
%patch1 -p1 -b .install

%if %{build_diet}
%patch2 -p1 -b .DIET
%ifarch x86_64
perl -pi -e "s|lib-i386|lib-x86_64|g" Makefile.dietlibc
%endif
%endif

cp %{SOURCE1} udhcpd.conf
cp %{SOURCE2} udhcpd.init

%build
%serverbuild

%if %{build_diet}
make -f Makefile.dietlibc
%else
make
%endif

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/var/lib/udhcpd

%makeinstall_std

install -m0644 udhcpd.conf %{buildroot}%{_sysconfdir}/udhcpd.conf
install -m0755 udhcpd.init %{buildroot}%{_initrddir}/udhcpd

touch %{buildroot}/var/lib/udhcpd/udhcpd.leases

%post -n udhcpd
%_post_service udhcpd
# New udhcpd lease file
if [ ! -f /var/lib/udhcpd/udhcpd.leases ]; then
    touch /var/lib/udhcpd/udhcpd.leases
fi

%preun -n udhcpd
%_preun_service udhcpd

%clean
rm -rf %{buildroot}

%files -n udhcpd
%defattr(-,root,root)
%doc README COPYING AUTHORS TODO samples/udhcpd.conf
%config(noreplace) %{_sysconfdir}/udhcpd.conf
%{_initrddir}/udhcpd
%dir /var/lib/udhcpd/
%config(noreplace) %ghost /var/lib/udhcpd/udhcpd.leases
%{_sbindir}/udhcpd
%{_bindir}/dumpleases
%{_mandir}/man1/dumpleases.*
%{_mandir}/man5/udhcpd.conf.*
%{_mandir}/man8/udhcpd.*

%files -n udhcpc
%defattr(-,root,root)
%doc README COPYING AUTHORS TODO samples/sample*
/sbin/udhcpc
%{_sysconfdir}/udhcpc
%{_mandir}/man8/udhcpc.*
