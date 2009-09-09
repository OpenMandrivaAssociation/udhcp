# OE: conditional switches
#
#(ie. use with rpm --rebuild):
#
#	--with diet	Compile udhcp against dietlibc


%define build_diet 0

# commandline overrides:
# rpm -ba|--rebuild --with 'xxx'
%{?_with_diet: %{expand: %%define build_diet 1}}

Summary:	Very small DHCP server/client
Name:		udhcp
Version:	0.9.8
Release:	%mkrel 13
License:	GPL
Group:		System/Servers
URL:		http://udhcp.busybox.net/
Source0:	http://udhcp.busybox.net/source/%{name}-%{version}.tar.bz2
Source1:	udhcpd.conf
Source2:	udhcpd.init
Patch0:		%{name}-0.9.7-Makefile.patch
Patch2:		udhcp-0.9.8-gcc3_4.patch
# http://www.lart.info/~bwachter/projects/dietlinux/download/current/patches/udhcp-0.9.8-dietlibc.patch
# P1 is rediffed for system dietlibc (only Makefile.dietlibc)
Patch1:		udhcp-0.9.8-dietlibc.patch
Patch3:		udhcp-rootpath_fix.diff
Patch4:		udhcp-0.9.8-altport.diff
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

%setup -q
%patch0 -p0
%patch2 -p1 -b .gcc3_4

%if %{build_diet}
%patch1 -p1 -b .DIET
%ifarch x86_64
perl -pi -e "s|lib-i386|lib-x86_64|g" Makefile.dietlibc
%endif
%endif

%patch3 -p0
%patch4 -p1

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
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/udhcpd.conf
%attr(755,root,root) %{_initrddir}/udhcpd
%dir /var/lib/udhcpd/
%config(noreplace) %ghost /var/lib/udhcpd/udhcpd.leases
%{_sbindir}/udhcpd
%{_bindir}/dumpleases
%{_mandir}/man1/dumpleases.*
%{_mandir}/man5/udhcpd.conf.*
%{_mandir}/man8/udhcpd.*

%files -n  udhcpc
%defattr(-,root,root)
%doc README COPYING AUTHORS TODO samples/sample*
/sbin/udhcpc
%dir %{_datadir}/udhcpc/
%{_datadir}/udhcpc/default.*
%{_mandir}/man8/udhcpc.*
