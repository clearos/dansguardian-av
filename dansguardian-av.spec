Name: dansguardian-av
Version: 2.10.1.1
Release: 11%dist
Group: Applications/Filtering
Summary: DansGuardian - Web filtering software
Vendor: DansGuardian
Source: dansguardian-%{version}.tar.gz
Source1: dansguardian-av.service
Source2: dansguardian.conf
Source3: dansguardianf1.conf
Source4: dansguardian-clamdscan.conf
Source5: dansguardian.logrotate
Source6: dansguardian-cleanup
Source20: dansguardian-bannedsitelist 
Source21: dansguardian-bannedurllist
Source22: dansguardian-weightedphraselist
Source23: dansguardian-bannedregexpurllist
Source24: dansguardian-exceptionvirusmimetypelist
Source25: dansguardian-exceptionmimetypelist
Patch1: dansguardian-gcc44.patch
Patch2: dansguardian-system-group.patch
Patch3: dansguardian-2.10.1.1-epoll.patch
Patch4: dansguardian-2.10.1.1-termfix.patch
Patch5: dansguardian-2.10.1.1-ntlmfix.patch
Patch100: dansguardian-2.10.1.1-avscan.patch
License: DansGuardian
Requires: dansguardian-phraselists >= 2.9
Requires: squid, pcre >= 6.0, clamav-server >= 0.95
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires(post): systemd-units
BuildRequires: gcc-c++, zlib-devel, which, pcre-devel
BuildRequires: pkgconfig
BuildRequires: systemd
Obsoletes: DansGuardian
BuildRoot: /tmp/%{name}-build

%description
DansGuardian - Web filtering software

%prep
%setup -q -n dansguardian-%{version}
%patch1 -p1 -b .gcc4
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch100 -p1
%build
./configure \
	--prefix=/usr \
	--sysconfdir=/etc \
	--datarootdir=/etc \
	--docdir=/doc \
	--mandir=%{_mandir} \
	--with-logdir=%{_localstatedir}/log/dansguardian \
	--with-proxyuser=dansguardian \
	--with-proxygroup=dansguardian \
	--program-suffix=-av \
	--disable-dependency-tracking \
    --with-dgdebug=off \
	--enable-clamd \
    --enable-kavd \
	--enable-fancydm \
	--enable-trickledm \
	--enable-ntlm \
	--enable-email

%{__perl} -pi.orig -e 's|/usr/lib|%{_libdir}|g' Makefile

make

%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot}

mkdir -p -m 755 %{buildroot}%{_localstatedir}/cache/dansguardian
mkdir -p -m 755 %{buildroot}%{_localstatedir}/lib/dansguardian
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p -m 755 %{buildroot}%{_sbindir}

# Move config to new directory
mv %{buildroot}%{_sysconfdir}/dansguardian %{buildroot}%{_sysconfdir}/dansguardian-av

# Link the phraselists and blacklists
rm -rf %{buildroot}%{_sysconfdir}/dansguardian-av/lists/blacklists
rm -rf %{buildroot}%{_sysconfdir}/dansguardian-av/lists/phraselists

# Install configuration files
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/dansguardian-av/dansguardian.conf
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/dansguardian-av/dansguardian.conf.default
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/dansguardian-av/dansguardianf1.conf
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/dansguardian-av/contentscanners/clamdscan.conf
install -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/dansguardian-av
install -m 755 %{SOURCE6} %{buildroot}%{_sbindir}/dansguardian-cleanup

install -m 644 %{SOURCE20} %{buildroot}%{_sysconfdir}/dansguardian-av/lists/bannedsitelist
install -m 644 %{SOURCE21} %{buildroot}%{_sysconfdir}/dansguardian-av/lists/bannedurllist
install -m 644 %{SOURCE22} %{buildroot}%{_sysconfdir}/dansguardian-av/lists/weightedphraselist
install -m 644 %{SOURCE23} %{buildroot}%{_sysconfdir}/dansguardian-av/lists/bannedregexpurllist
install -m 644 %{SOURCE24} %{buildroot}%{_sysconfdir}/dansguardian-av/lists/contentscanners/exceptionvirusmimetypelist
install -m 644 %{SOURCE25} %{buildroot}%{_sysconfdir}/dansguardian-av/lists/exceptionmimetypelist

# Touch missing files
touch %{buildroot}%{_sysconfdir}/dansguardian-av/lists/exceptionfileurllist
touch %{buildroot}%{_sysconfdir}/dansguardian-av/lists/logurllist
touch %{buildroot}%{_sysconfdir}/dansguardian-av/lists/logsitelist
touch %{buildroot}%{_sysconfdir}/dansguardian-av/lists/logregexpurllist
touch %{buildroot}%{_sysconfdir}/dansguardian-av/lists/bannedregexpheaderlist
touch %{buildroot}%{_sysconfdir}/dansguardian-av/lists/headerregexplist


# Configure has %docdir setting... let RPM do its thing in the %file section
rm -rf %{buildroot}/doc

# Create log directory to make logrotate happy
ln -s %{_localstatedir}/log/dansguardian %{buildroot}%{_localstatedir}/log/dansguardian-av

# Cleanup unwanted files and directories
rm -rf %{buildroot}%{_sysconfdir}/dansguardian-av/dansguardian.pl
rm -rf %{buildroot}%{_sysconfdir}/dansguardian-av/scripts
rm -rf %{buildroot}%{_sysconfdir}/dansguardian-av/contentscanners/kavdscan.conf
rm -rf %{buildroot}/usr/lib
rm -rf %{buildroot}/usr/src

# Install systemd script
mkdir -p -m 755 %{buildroot}/usr/lib/systemd/system
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/dansguardian-av.service

# Fix configuration paths (TODO: investigate DGCONFDIR environment variable)
CONFIGS="contentscanners/clamdscan.conf downloadmanagers/fancy.conf lists/weightedphraselist \
	lists/bannedsitelist lists/bannedurllist authplugins/ip.conf"
for CONFIG in $CONFIGS; do
	sed -i -e 's/\/etc\/dansguardian\//\/etc\/dansguardian-av\//' %{buildroot}%{_sysconfdir}/dansguardian-av/$CONFIG
done

# Fix configuration files
sed -i -e 's/^\.Include.*//' %{buildroot}%{_sysconfdir}/dansguardian-av/lists/exceptionphraselist
sed -i -e 's/^\.Include.*//' %{buildroot}%{_sysconfdir}/dansguardian-av/lists/bannedphraselist
echo "" > %{buildroot}%{_sysconfdir}/dansguardian-av/lists/bannedmimetypelist
echo "" > %{buildroot}%{_sysconfdir}/dansguardian-av/lists/bannedextensionlist

%pre
getent group dansguardian >/dev/null || groupadd -r dansguardian
getent passwd dansguardian >/dev/null || \
    useradd -r -g dansguardian -d %{_localstatedir}/log/dansguardian -s /sbin/nologin \
    -c "DansGuardian" dansguardian
exit 0

%post
%systemd_post dansguardian-av.service

if [ -e %{_sysconfdir}/dansguardian-av/dansguardian.conf ]; then
	sed -i -e "s/^contentscanner.*contentscanners\/clamav.conf.*/contentscanner = '\/etc\/dansguardian-av\/contentscanners\/clamdscan.conf'/" %{_sysconfdir}/dansguardian-av/dansguardian.conf
	sed -i -e "s/^daemongroup[[:space:]]=.*/daemongroup = 'clam'/" %{_sysconfdir}/dansguardian-av/dansguardian.conf
fi

exit 0

%postun
%systemd_postun dansguardian-av.service

exit 0

%preun
%systemd_preun dansguardian-av.service

exit 0

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc doc/AuthPlugins doc/ContentScanners doc/DownloadManagers doc/FAQ doc/FAQ.html doc/Plugins
%config(noreplace) %{_sysconfdir}/dansguardian-av/dansguardian.conf
%config(noreplace) %{_sysconfdir}/dansguardian-av/dansguardianf1.conf
%config(noreplace) %{_sysconfdir}/dansguardian-av/lists
%config(noreplace) %{_sysconfdir}/dansguardian-av/languages/*/template.html
%config(noreplace) %{_sysconfdir}/dansguardian-av/languages/*/fancydmtemplate.html
%{_sysconfdir}/dansguardian-av/languages
%{_sysconfdir}/dansguardian-av/authplugins
%{_sysconfdir}/dansguardian-av/contentscanners
%{_sysconfdir}/dansguardian-av/downloadmanagers
%{_sysconfdir}/dansguardian-av/dansguardian.conf.default
%{_sysconfdir}/dansguardian-av/transparent1x1.gif
%{_sysconfdir}/logrotate.d/dansguardian-av
%{_sbindir}/dansguardian-av
%{_sbindir}/dansguardian-cleanup
%{_mandir}/man8/dansguardian-av.8.gz
%attr(755,dansguardian,dansguardian) %dir %{_localstatedir}/cache/dansguardian
%attr(755,dansguardian,dansguardian) %dir %{_localstatedir}/lib/dansguardian
%attr(750,dansguardian,dansguardian) %dir %{_localstatedir}/log/dansguardian
%{_localstatedir}/log/dansguardian-av
/usr/lib/systemd/system/dansguardian-av.service

%changelog
* Tue Sep 23 2014 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-11
* added systemd support

* Fri Apr 18 2014 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-10
- added NTLM fix for ClearOS 7 build fix

* Mon Sep  9 2013 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-9
- enhanced antivirus scan logging
- updated MIME lists

* Fri Mar 22 2013 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-8
- enabled epoll patch

* Mon Feb 25 2013 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-7
- disabled epoll patch

* Thu Jun 14 2012 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-6
- added epoll patch

* Mon Jan  2 2012 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-5
- changed ClamAV socket path

* Thu Dec  8 2011 ClearFoundation <developer@clearfoundation.com> 2.10.1.1-4
- started packaging changelog
