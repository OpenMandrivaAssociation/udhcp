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
Release:	0.%{snapshot}.3
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
%make -f Makefile.dietlibc STRIP=/bin/true
%else
%make STRIP=/bin/true
%endif

%install
install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/var/lib/udhcpd

%makeinstall_std STRIP=/bin/true

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

%files -n udhcpd
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
%doc README COPYING AUTHORS TODO samples/sample*
/sbin/udhcpc
%{_sysconfdir}/udhcpc
%{_mandir}/man8/udhcpc.*


%changelog
* Wed Dec 08 2010 Oden Eriksson <oeriksson@mandriva.com> 0.9.9-0.20050303.2mdv2011.0
+ Revision: 615286
- the mass rebuild of 2010.1 packages

* Sun Nov 08 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.9.9-0.20050303.1mdv2010.1
+ Revision: 463256
- update to last CVS snapshot before merge in busybox
- install scripts under /etc, as it is quite useless for the client to be
  in /sbin otherwise
- fix default script

* Wed Sep 09 2009 Thierry Vignaud <tv@mandriva.org> 0.9.8-13mdv2010.0
+ Revision: 434496
- rebuild

* Sat Sep 20 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8-12mdv2009.0
+ Revision: 286255
- ported the altport patch from the mille-xterm-busybox package
- fix dietlibc build

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 0.9.8-11mdv2009.0
+ Revision: 269444
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Oden Eriksson <oeriksson@mandriva.com>
    - added lsb headers to the init script

* Fri May 16 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8-10mdv2009.0
+ Revision: 208116
- added P3 to attempt to fix #40789

* Wed Jan 02 2008 Olivier Blin <oblin@mandriva.com> 0.9.8-9mdv2008.1
+ Revision: 140924
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Tue Dec 12 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8-9mdv2007.0
+ Revision: 95916
- Import udhcp

* Tue Dec 12 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8-9mdv2007.1
- bunzip sources and patches

* Thu Jan 05 2006 Lenny Cartier <lenny@mandriva.com> 0.9.8-8mdk
- rebuild

* Sun Oct 31 2004 Christiaan Welvaart <cjw@daneel.dyndns.org> 0.9.8-7mdk
- patch2: fix build with gcc 3.4

