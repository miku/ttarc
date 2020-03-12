Summary:    TikTok trending to WARC.
Name:       ttarc
Version:    0.1.0
Release:    0
License:    GPL
ExclusiveArch:  x86_64
BuildRoot:  %{_tmppath}/%{name}-build
Group:      System/Base
Vendor:     Archiving Tools
URL:        https://github.com/miku/ttarc

%description

TikTok trending to WARC.

%prep

%build

%pre

%install

mkdir -p $RPM_BUILD_ROOT/usr/local/bin
install -m 755 ttarc $RPM_BUILD_ROOT/usr/local/bin

%post

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf %{_tmppath}/%{name}
rm -rf %{_topdir}/BUILD/%{name}

%files
%defattr(-,root,root)

/usr/local/bin/ttarc

%changelog

* Thu Mar 12 2020 Martin Czygan
- 0.1.0 release
