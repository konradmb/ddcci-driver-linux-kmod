# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod

%global debug_package %{nil}

# name should have a -kmod suffix
Name:           ddcci-driver-linux-kmod

Version:        0.4.3.master+mr12
Release:        1%{?dist}.1
Summary:        Kernel module(s)

Group:          System Environment/Kernel

License:        GPL-2
URL:            https://gitlab.com/ddcci-driver-linux/ddcci-driver-linux
Source0:        https://gitlab.com/ddcci-driver-linux/ddcci-driver-linux/-/archive/merge-requests/12/head/ddcci-driver-linux.tar.gz

BuildRequires:  %{_bindir}/kmodtool


# Verify that the package build for all architectures.
# In most time you should remove the Exclusive/ExcludeArch directives
# and fix the code (if needed).
# ExclusiveArch:  i686 x86_64 ppc64 ppc64le armv7hl aarch64
# ExcludeArch: i686 x86_64 ppc64 ppc64le armv7hl aarch64

# get the proper build-sysbuild package from the repo, which
# tracks in all the kernel-devel packages
BuildRequires:  %{_bindir}/kmodtool

%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


%description


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
#kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null
kmodtool  --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T -a 0

# apply patches and do other stuff here
# pushd foo-%{version}
# #patch0 -p1 -b .suffix
# popd

mv ddcci-driver-linux-* ddcci-driver-linux
ls

for kernel_version in %{?kernel_versions} ; do
    cp -a ddcci-driver-linux _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${kernel_version##*___}" M=${PWD}/_kmod_build_${kernel_version%%___*}/ddcci modules
    make %{?_smp_mflags} -C "${kernel_version##*___}" M=${PWD}/_kmod_build_${kernel_version%%___*}/ddcci-backlight modules
done


%install
rm -rf ${RPM_BUILD_ROOT}

for kernel_version in %{?kernel_versions}; do
    # make install DESTDIR=${RPM_BUILD_ROOT} KMODPATH=%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ddcci
    # make install DESTDIR=${RPM_BUILD_ROOT} KMODPATH=%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ddcci-backlight
    install -D -m 755 _kmod_build_${kernel_version%%___*}/ddcci/ddcci.ko  ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ddcci/ddcci.ko
    install -D -m 755 _kmod_build_${kernel_version%%___*}/ddcci-backlight/ddcci-backlight.ko  ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ddcci-backlight/ddcci-backlight.ko
done
%{?akmod_install}

cat > ddcci-driver-linux.conf <<'EOF'
ddcci
ddcci-backlight
EOF

mkdir -p %{buildroot}/usr/lib/modules-load.d/
install -m 0755 ddcci-driver-linux.conf %{buildroot}/usr/lib/modules-load.d/


%clean
rm -rf $RPM_BUILD_ROOT


%changelog
%autochangelog

%package common
Summary:    Kernel module(s)

%description common

%files common
/usr/lib/modules-load.d/ddcci-driver-linux.conf