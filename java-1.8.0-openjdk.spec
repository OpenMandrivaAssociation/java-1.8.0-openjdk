# If debug is 1, OpenJDK is built with all debug info present.
%global debug 0
%global _jvmdir /usr/lib/jvm

%if %mdvver <= 3000000
# not defined on 3.0
%global aarch64         aarch64 arm64 armv8
%global x86_64          x86_64
%else
# macro removed from javapackages
%global _jvmjardir     %{_prefix}/lib/jvm-exports
%endif

%global multilib_arches %{power64} sparc64 %{x86_64} %{aarch64}
%global jit_arches      %{ix86} %{x86_64} sparcv9 sparc64 %{aarch64}

%ifarch %{arm}
# Bug in dwz? causes infinite loop in dwz with openjdk
%define _find_debuginfo_dwz_opts %{nil}
%endif

# sometimes we need to distinguish big and little endian PPC64
# taken from the openjdk-1.7 spec
%global ppc64le                 ppc64le
%global ppc64be                 ppc64 ppc64p7

%ifarch %{x86_64}
%global archinstall amd64
%endif
%ifarch ppc
%global archinstall ppc
%endif
%ifarch %{power64}
%global archinstall ppc64
%endif
%ifarch %{ppc64le}
%global archinstall ppc64le
%endif
%ifarch %{ix86}
%global archinstall i386
%endif
%ifarch ia64
%global archinstall ia64
%endif
%ifarch s390
%global archinstall s390
%endif
%ifarch s390x
%global archinstall s390x
%endif
%ifarch %{arm}
%global archinstall arm
%endif
%ifarch %{aarch64}
%global archinstall aarch64
%endif
# 32 bit sparc, optimized for v9
%ifarch sparcv9
%global archinstall sparc
%endif
# 64 bit sparc
%ifarch sparc64
%global archinstall sparcv9
%endif
%ifnarch %{jit_arches}
%global archinstall %{_arch}
%endif

%if %{debug}
%global debugbuild slowdebug
%else
%global debugbuild release
%endif

%global buildoutputdir openjdk/build/jdk8.build

%ifarch %{jit_arches}
%global with_systemtap 1
%else
%global with_systemtap 0
%endif

# Convert an absolute path to a relative path.  Each symbolic link is
# specified relative to the directory in which it is installed so that
# it will resolve properly within chrooted installations.
%global script 'use File::Spec; print File::Spec->abs2rel($ARGV[0], $ARGV[1])'
%global abs2rel perl -e %{script}

# Hard-code libdir on 64-bit architectures to make the 64-bit JDK
# simply be another alternative.
%global LIBDIR %{_libdir}
#backuped original one
%ifarch %{multilib_arches}
%global syslibdir       %{_prefix}/lib64
%global _libdir         %{_prefix}/lib
%global archname        %{name}.%{_arch}
%else
%global syslibdir       %{_libdir}
%global archname        %{name}
%endif

# Standard JPackage naming and versioning defines.
%global origin          openjdk
# note, following three variables are sedded from update_sources if used correctly. Hardcode them rather there.
%global project         aarch64-port
%global repo            jdk8u-shenandoah
# Current version should be listed at
# http://openjdk.java.net/projects/jdk8u/ or http://hg.openjdk.java.net/aarch64-port/jdk8u/tags
%global revision        aarch64-shenandoah-jdk8u302-b08
# eg # jdk8u60-b27 -> jdk8u60 or # aarch64-jdk8u60-b27 -> aarch64-jdk8u60  (dont forget spec escape % by %%)
%global whole_update    %(VERSION=%{revision}; echo ${VERSION%%-*})
# eg  jdk8u60 -> 60 or aarch64-jdk8u60 -> 60
%global updatever       %(VERSION=%{whole_update}; echo ${VERSION##*u})
# eg jdk8u60-b27 -> b27
%global buildver        %(VERSION=%{revision}; echo ${VERSION##*-})
# priority must be 7 digits in total. The expression is workarounding tip
%global priority        %(TIP=1800%{updatever};  echo ${TIP/tip/99})

%global javaver         1.8.0

# Standard JPackage directories and symbolic links.
# Make 64-bit JDKs just another alternative on 64-bit architectures.
%ifarch %{multilib_arches}
%global sdklnk          java-%{javaver}-%{origin}.%{_arch}
%global jrelnk          jre-%{javaver}-%{origin}.%{_arch}
%global sdkdir          %{name}-%{version}.%{_arch}
%else
%global sdklnk          java-%{javaver}-%{origin}
%global jrelnk          jre-%{javaver}-%{origin}
%global sdkdir          %{name}-%{version}
%endif
%global jredir          %{sdkdir}/jre
%global sdkbindir       %{_jvmdir}/%{sdklnk}/bin
%global jrebindir       %{_jvmdir}/%{jrelnk}/bin
%ifarch %{multilib_arches}
%global jvmjardir       %{_jvmjardir}/%{name}-%{version}.%{_arch}
%else
%global jvmjardir       %{_jvmjardir}/%{name}-%{version}
%endif

%if %{with_systemtap}
# Where to install systemtap tapset (links)
# We would like these to be in a package specific subdir,
# but currently systemtap doesn't support that, so we have to
# use the root tapset dir for now. To distinquish between 64
# and 32 bit architectures we place the tapsets under the arch
# specific dir (note that systemtap will only pickup the tapset
# for the primary arch for now). Systemtap uses the machine name
# aka build_cpu as architecture specific directory name.
%global tapsetroot /usr/share/systemtap
%global tapsetdir %{tapsetroot}/tapset/%{_build_cpu}
%endif

# Prevent brp-java-repack-jars from being run.
%global __jar_repack 0

Name:    java-%{javaver}-%{origin}
Version: %{javaver}.%{updatever}
Release: 0.%{buildver}
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons,
# and this change was brought into RHEL-4.  java-1.5.0-ibm packages
# also included the epoch in their virtual provides.  This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0".  In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0.  So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages.  Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".
Epoch:   1
Summary: OpenJDK Runtime Environment
Group:   Development/Java

License:  ASL 1.1 and ASL 2.0 and GPL+ and GPLv2 and GPLv2 with exceptions and LGPL+ and LGPLv2 and MPLv1.0 and MPLv1.1 and Public Domain and W3C
URL:      https://openjdk.java.net/

# Source from upstrem OpenJDK8 project. To regenerate, use
# aarch64-port now contains integration forest of both aarch64 and normal jdk
# PROJECT_NAME=aarch64-port REPO_NAME=jdk8u VERSION=aarch64-jdk8u181-b15 ./generate_source_tarball.sh
Source0: %{project}-%{repo}-%{revision}-4curve.tar.xz

# Custom README for -src subpackage
Source2:  README.src

Source3:  java-abrt-launcher.in

# Use 'generate_tarballs.sh' to generate the following tarballs
# They are based on code contained in the IcedTea7 project.

# Systemtap tapsets. Zipped up to keep it small.
Source8: systemtap-tapset-3.6.0pre02.tar.xz

# Desktop files. Adapated from IcedTea.
Source9: jconsole.desktop.in
Source10: policytool.desktop.in

# nss configuration file
Source11: nss.cfg

# Removed libraries that we link instead
Source12: remove-intree-libraries.sh

# Ensure we aren't using the limited crypto policy
Source13: TestCryptoLevel.java

Source14: TestECDSA.java

Source200: java-1.8.0-openjdk.rpmlintrc

# Upstreamable patches
# PR2737: Allow multiple initialization of PKCS11 libraries
Patch5: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/multiple-pkcs11-library-init.patch

# Similar for GCC 11
	
Patch112: %{name}-gcc11.patch

# PR2095, RH1163501: 2048-bit DH upper bound too small for Fedora infrastructure (sync with IcedTea 2.x)
Patch504: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/rh1163501.patch
# S4890063, PR2304, RH1214835: HPROF: default text truncated when using doe=n option
Patch511: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/rh1214835.patch
# Turn off strict overflow on IndicRearrangementProcessor{,2}.cpp following 8140543: Arrange font actions
Patch512: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/no_strict_overflow.patch

# S8150954, RH1176206, PR2866: Taking screenshots on x11 composite desktop produces wrong result
# In progress: http://mail.openjdk.java.net/pipermail/awt-dev/2016-March/010742.html
Patch508: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/rh1176206-jdk.patch
Patch509: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/rh1176206-root.patch

# RH1337583, PR2974: PKCS#10 certificate requests now use CRLF line endings rather than system line endings
Patch523: pr2974-rh1337583-add_systemlineendings_option_to_keytool_and_use_line_separator_instead_of_crlf_in_pkcs10.patch

# PR3083, RH1346460: Regression in SSL debug output without an ECC provider
Patch528: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/pr3083-rh1346460-for_ssl_debug_return_null_instead_of_exception_when_theres_no_ecc_provider.patch


# 8196516, RH1538767: libfontmanager.so needs to be built with LDFLAGS so as to allow
#                     linking with unresolved symbols.
Patch529: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/rhbz_1538767_fix_linking2.patch

# Upstreamable debugging patches
# Patches 204 and 205 stop the build adding .gnu_debuglink sections to unstripped files
#Patch204: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/hotspot-remove-debuglink.patch
Patch205: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/dont-add-unnecessary-debug-links.patch
# Enable debug information for assembly code files
Patch206: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/hotspot-assembler-debuginfo.patch
# Arch-specific upstreamable patches
# PR2415: JVM -Xmx requirement is too high on s390
Patch100: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/%{name}-s390-java-opts.patch
# Patches which need backporting to 8u
# S8073139, RH1191652; fix name of ppc64le architecture
Patch601: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/%{name}-rh1191652-root.patch
Patch602: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/%{name}-rh1191652-jdk.patch
Patch603: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/%{name}-rh1191652-hotspot-aarch64.patch
# Include all sources in src.zip
Patch7: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/include-all-srcs.patch
# 8035341: Allow using a system installed libpng
Patch202: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/system-libpng.patch
# 8042159: Allow using a system-installed lcms2
Patch203: jdk8042159-allow_using_system_installed_lcms2-root.patch
Patch204: jdk8042159-allow_using_system_installed_lcms2-jdk.patch
# PR2462: Backport "8074839: Resolve disabled warnings for libunpack and the unpack200 binary"
# This fixes printf warnings that lead to build failure with -Werror=format-security from optflags
Patch502: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/pr2462.patch
# S8148351, PR2842: Only display resolved symlink for compiler, do not change path
Patch506: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/pr2842-01.patch
Patch507: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/pr2842-02.patch
# S6260348, PR3066: GTK+ L&F JTextComponent not respecting desktop caret blink rate
Patch526: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/6260348-pr3066.patch
# 8061305, PR3335, RH1423421: Javadoc crashes when method name ends with "Property"
Patch538: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/8061305-pr3335-rh1423421.patch
Patch540: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/rhbz1548475-LDFLAGSusage.patch

# 8188030, PR3459, RH1484079: AWT java apps fail to start when some minimal fonts are present
Patch560: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/8188030-pr3459-rh1484079.patch

# 8197429, PR3456, RH153662{2,3}: 32 bit java app started via JNI crashes with larger stack sizes
Patch561: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/8197429-pr3456-rh1536622.patch

# Patches ineligible for 8u
# 8043805: Allow using a system-installed libjpeg
Patch201: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/system-libjpeg.patch
Patch210: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/suse_linuxfilestore.patch

# custom securities
Patch300: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/PR3183.patch

# Turn on AssumeMP by default on RHEL systems
Patch534: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/always_assumemp.patch

# PR2888: OpenJDK should check for system cacerts database (e.g. /etc/pki/java/cacerts)
Patch539: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/pr2888-openjdk_should_check_for_system_cacerts_database_eg_etc_pki_java_cacerts.patch

# Shenandoah fixes

# PR3573: Fix TCK crash with Shenandoah
Patch700: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/pr3573.patch

# Non-OpenJDK fixes
Patch1000: https://src.fedoraproject.org/rpms/java-1.8.0-openjdk/raw/master/f/enableCommentedOutSystemNss.patch

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: pkgconfig(alsa)
BuildRequires: binutils
BuildRequires: cups-devel
BuildRequires: desktop-file-utils
BuildRequires: fontconfig
BuildRequires: freetype-devel
BuildRequires: giflib-devel
BuildRequires: gcc-c++
BuildRequires: pkgconfig(gtk+-2.0)
BuildRequires: pkgconfig(lcms2)
#BuildRequires: javapackages-local
BuildRequires: jpeg-devel
BuildRequires: pkgconfig(libpng)
BuildRequires: perl
BuildRequires: xsltproc
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xi)
BuildRequires: pkgconfig(xcomposite)
BuildRequires: pkgconfig(xinerama)
BuildRequires: pkgconfig(xt)
BuildRequires: pkgconfig(xtst)
BuildRequires: pkgconfig
BuildRequires: pkgconfig(xproto)
#BuildRequires: redhat-lsb
BuildRequires: zip
# OpenJDK X officially requires OpenJDK (X-1) to build
BuildRequires: java-1.8.0-openjdk-devel
# Zero-assembler build requirement.
%ifnarch %{jit_arches}
BuildRequires: pkgconfig(libffi)
%endif

# cacerts build requirement.
BuildRequires: openssl
# execstack build requirement.
# no prelink on ARM yet
%ifnarch %{arm} %{aarch64} ppc64le
#BuildRequires: prelink
%endif
%if %{with_systemtap}
BuildRequires: systemtap
%endif

# Requires rest of java
Requires: %{name}-headless = %{epoch}:%{version}-%{release}

# Standard JPackage base provides.
Provides: jre-%{javaver}-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver} = %{epoch}:%{version}-%{release}
Provides: jre = %{javaver}
Provides: java-%{origin} = %{epoch}:%{version}-%{release}
Provides: java = %{epoch}:%{javaver}
# Standard JPackage extensions provides.
Provides: java-fonts = %{epoch}:%{version}

%description
The OpenJDK runtime environment.


%package headless
Summary: OpenJDK Runtime Environment
Group:   Development/Java

# Require /etc/pki/java/cacerts.
Requires: rootcerts-java
# Require javapackages-tools for ownership of /usr/lib/jvm/
Requires: javapackages-tools
# Require zoneinfo data provided by tzdata-java subpackage.
Requires: tzdata-java
# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage base provides.
Provides: jre-%{javaver}-%{origin}-headless = %{epoch}:%{version}-%{release}
Provides: jre-%{origin}-headless = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}-headless = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-headless = %{epoch}:%{version}-%{release}
Provides: jre-headless = %{javaver}
Provides: java-%{origin}-headless = %{epoch}:%{version}-%{release}
Provides: java-headless = %{epoch}:%{javaver}
# Standard JPackage extensions provides.
Provides: jndi = %{epoch}:%{version}
Provides: jndi-ldap = %{epoch}:%{version}
Provides: jndi-cos = %{epoch}:%{version}
Provides: jndi-rmi = %{epoch}:%{version}
Provides: jndi-dns = %{epoch}:%{version}
Provides: jaas = %{epoch}:%{version}
Provides: jsse = %{epoch}:%{version}
Provides: jce = %{epoch}:%{version}
Provides: jdbc-stdext = 4.1
Provides: java-sasl = %{epoch}:%{version}

%description headless
The OpenJDK runtime environment without audio and video support.


%package devel
Summary: OpenJDK Development Environment
Group:   Development/Java

# Require base package.
Requires:         %{name} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage devel provides.
Provides: java-sdk-%{javaver}-%{origin} = %{epoch}:%{version}
Provides: java-sdk-%{javaver} = %{epoch}:%{version}
Provides: java-sdk-%{origin} = %{epoch}:%{version}
Provides: java-sdk = %{epoch}:%{javaver}
Provides: java-%{javaver}-devel = %{epoch}:%{version}
Provides: java-devel-%{origin} = %{epoch}:%{version}
Provides: java-devel = %{epoch}:%{javaver}


%description devel
The OpenJDK development tools.

%package demo
Summary: OpenJDK Demos
Group:   Development/Java

Requires: %{name} = %{epoch}:%{version}-%{release}

%description demo
The OpenJDK demos.

%package src
Summary: OpenJDK Source Bundle
Group:   Development/Java

Requires: %{name} = %{epoch}:%{version}-%{release}

%description src
The OpenJDK source bundle.

%package javadoc
Summary: OpenJDK API Documentation
Group:   Development/Java
Requires: javapackages-tools
BuildArch: noarch

# Post requires alternatives to install javadoc alternative.
Requires(post):   %{_sbindir}/alternatives
# Postun requires alternatives to uninstall javadoc alternative.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage javadoc provides.
Provides: java-javadoc = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-javadoc = %{epoch}:%{version}-%{release}

%description javadoc
The OpenJDK API documentation.


%prep
%setup -q -c -n %{name} -T -a 0

# Compatibility with old patches
ln -s openjdk jdk8

cp %{SOURCE2} .

# replace outdated configure guess script
#
# the configure macro will do this too, but it also passes a few flags not
# supported by openjdk configure script
cp %{_datadir}/automake-*/config.guess openjdk/common/autoconf/build-aux/
cp %{_datadir}/automake-*/config.sub openjdk/common/autoconf/build-aux/

# OpenJDK patches

# System library fixes
%patch201
%patch202
%patch203
%patch204

# Debugging fixes
#patch204
#patch205
%patch206
#patch210
%patch300
%patch5
#patch7

# s390 build fixes
#patch100

# ppc64le fixes
%patch603
#patch601
#patch602

# Zero fixes.

# Upstreamable fixes
%patch502
%patch504
#patch506
#patch507
#patch508
#patch509
%patch511
#patch512
%patch523
#patch526
%patch528
#patch538
#patch540 -p1 -b .0540~
#patch560
pushd openjdk/jdk
#patch529 -p1
popd
#patch561
%patch112

# RPM-only fixes
%patch539

# Shenandoah-only patches
%if 0
%patch700
%endif
%patch1000

# Extract systemtap tapsets
%if %{with_systemtap}

tar xzf %{SOURCE8}

for file in tapset/*.in; do

    OUTPUT_FILE=`echo $file | sed -e s:\.in$::g`
    sed -e s:@ABS_SERVER_LIBJVM_SO@:%{_jvmdir}/%{sdkdir}/jre/lib/%{archinstall}/server/libjvm.so:g $file > $file.1
# TODO find out which architectures other than ix86 have a client vm
%ifarch %{ix86}
    sed -e s:@ABS_CLIENT_LIBJVM_SO@:%{_jvmdir}/%{sdkdir}/jre/lib/%{archinstall}/client/libjvm.so:g $file.1 > $OUTPUT_FILE
%else
    sed -e '/@ABS_CLIENT_LIBJVM_SO@/d' $file.1 > $OUTPUT_FILE
%endif
    sed -i -e s:@ABS_JAVA_HOME_DIR@:%{_jvmdir}/%{sdkdir}:g $OUTPUT_FILE
    sed -i -e s:@INSTALL_ARCH_DIR@:%{archinstall}:g $OUTPUT_FILE

done

%endif

# Prepare desktop files
for file in %{SOURCE9} %{SOURCE10} ; do
    OUTPUT_FILE=`basename $file | sed -e s:\.in$::g`
    sed -e s:@JAVA_HOME@:%{_jvmdir}/%{sdkdir}:g $file > $OUTPUT_FILE
    sed -i -e s:@VERSION@:%{version}-%{release}.%{_arch}:g $OUTPUT_FILE
done

%build
# How many cpu's do we have?
export NUM_PROC=`/usr/bin/getconf _NPROCESSORS_ONLN 2> /dev/null || :`
export NUM_PROC=${NUM_PROC:-1}

# Build IcedTea and OpenJDK.
%ifarch s390x sparc64 alpha %{power64}
export ARCH_DATA_MODEL=64
%endif
%ifarch alpha
export CFLAGS="$CFLAGS -mieee"
%endif

%ifarch %{arm}
# Let's see if this fixes the crash on startup when javac is launched
# for the first time...
export CC=gcc
export CXX=g++
%endif

# We use because the OpenJDK build seems to
# pass EXTRA_CFLAGS to the HotSpot C++ compiler...
# Explicitly set the C++ standard as the default has changed on GCC >= 6
EXTRA_CFLAGS=" -Wno-error -std=gnu++98 -fno-delete-null-pointer-checks -fno-lifetime-dse"
EXTRA_CPP_FLAGS=" -std=gnu++98 -fno-delete-null-pointer-checks -fno-lifetime-dse"
%ifarch %{ix86} %{arm}
EXTRA_CFLAGS="$EXTRA_CFLAGS -mincoming-stack-boundary=2"
EXTRA_CPP_FLAGS="$EXTRA_CPP_FLAGS -mincoming-stack-boundary=2"
%endif
export EXTRA_CFLAGS

(cd openjdk/common/autoconf
 bash ./autogen.sh
)

mkdir -p %{buildoutputdir}

pushd %{buildoutputdir}

bash ../../configure \
%ifnarch %{jit_arches}
    --with-jvm-variants=zero \
%endif
    --disable-zip-debug-info \
    --with-milestone="fcs" \
    --with-update-version=%{updatever} \
    --with-build-number=%{buildver} \
    --with-user-release-suffix="openmandriva-%{version}-%{release}" \
    --with-boot-jdk=/usr/lib/jvm/java-1.8.0 \
    --with-debug-level=%{debugbuild} \
    --enable-unlimited-crypto \
    --with-zlib=system \
    --with-libjpeg=system \
    --with-giflib=system \
    --with-libpng=system \
    --with-lcms=system \
    --with-stdc++lib=dynamic \
    --with-num-cores="$NUM_PROC" \
    --with-extra-cflags="$EXTRA_CFLAGS" \
    --with-extra-cxxflags="$EXTRA_CPP_FLAGS"

# The combination of FULL_DEBUG_SYMBOLS=0 and ALT_OBJCOPY=/does_not_exist
# disables FDS for all build configs and reverts to pre-FDS make logic.
# STRIP_POLICY=none says don't do any stripping. DEBUG_BINARIES=true says
# ignore all the other logic about which debug options and just do '-g'.

make \
    JOBS="`getconf _NPROCESSORS_ONLN`" \
    LCMS_LIBS="`pkg-config --libs lcms2`" \
    DEBUG_BINARIES=true \
    STRIP_POLICY=no_strip \
    POST_STRIP_CMD="" \
    LOG=trace \
    SCTP_WERROR= \
    all

# the build (erroneously) removes read permissions from some jars
# this is a regression in OpenJDK 7 (our compiler):
# http://icedtea.classpath.org/bugzilla/show_bug.cgi?id=1437
find images/j2sdk-image -iname '*.jar' -exec chmod ugo+r {} \;
chmod ugo+r images/j2sdk-image/lib/ct.sym

# remove redundant *diz and *debuginfo files
find images/j2sdk-image -iname '*.diz' -exec rm {} \;
find images/j2sdk-image -iname '*.debuginfo' -exec rm {} \;

popd >& /dev/null

export JAVA_HOME=$(pwd)/%{buildoutputdir}/images/j2sdk-image

# Install java-abrt-luncher
mv $JAVA_HOME/jre/bin/java $JAVA_HOME/jre/bin/java-abrt
cat %{SOURCE3} | sed -e s:@JAVA_PATH@:%{_jvmdir}/%{jredir}/bin/java-abrt:g -e s:@LIB_DIR@:%{LIBDIR}/libabrt-java-connector.so:g > $JAVA_HOME/jre/bin/java
chmod 755 $JAVA_HOME/jre/bin/java


# Copy tz.properties
echo "sun.zoneinfo.dir=/usr/share/javazi" >> $JAVA_HOME/jre/lib/tz.properties

# Check unlimited policy has been used
$JAVA_HOME/bin/javac -d . %{SOURCE13}
$JAVA_HOME/bin/java TestCryptoLevel

# Check ECC is working
$JAVA_HOME/bin/javac -d . %{SOURCE14}
$JAVA_HOME/bin/java $(echo $(basename %{SOURCE14})|sed "s|\.java||")

# Check debug symbols are present and can identify code
#nm -aCl $JAVA_HOME/jre/lib/%{archinstall}/server/libjvm.so | grep javaCalls.cpp

%install
rm -rf $RPM_BUILD_ROOT
STRIP_KEEP_SYMTAB=libjvm*

# Install symlink to default soundfont
install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/audio
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/audio
ln -s %{_datadir}/soundfonts/default.sf2
popd

pushd %{buildoutputdir}/images/j2sdk-image

  # Install main files.
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}
  cp -a bin include lib src.zip $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}
  cp -a jre/bin jre/lib $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}

%if %{with_systemtap}
  # Install systemtap support files.
  install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/tapset
  cp -a $RPM_BUILD_DIR/%{name}/tapset/*.stp $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/tapset/
  install -d -m 755 $RPM_BUILD_ROOT%{tapsetdir}
  pushd $RPM_BUILD_ROOT%{tapsetdir}
    RELATIVE=$(%{abs2rel} %{_jvmdir}/%{sdkdir}/tapset %{tapsetdir})
    ln -sf $RELATIVE/*.stp .
  popd
%endif

  # Install cacerts symlink.
  rm -f $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security/cacerts
  pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security
    RELATIVE=$(%{abs2rel} %{_sysconfdir}/pki/java \
      %{_jvmdir}/%{jredir}/lib/security)
    ln -sf $RELATIVE/cacerts .
  popd

  # Install extension symlinks.
  install -d -m 755 $RPM_BUILD_ROOT%{jvmjardir}
  pushd $RPM_BUILD_ROOT%{jvmjardir}
    RELATIVE=$(%{abs2rel} %{_jvmdir}/%{jredir}/lib %{jvmjardir})
    ln -sf $RELATIVE/jsse.jar jsse-%{version}.jar
    ln -sf $RELATIVE/jce.jar jce-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-ldap-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-cos-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-rmi-%{version}.jar
    ln -sf $RELATIVE/rt.jar jaas-%{version}.jar
    ln -sf $RELATIVE/rt.jar jdbc-stdext-%{version}.jar
    ln -sf jdbc-stdext-%{version}.jar jdbc-stdext-3.0.jar
    ln -sf $RELATIVE/rt.jar sasl-%{version}.jar
    for jar in *-%{version}.jar
    do
      if [ x%{version} != x%{javaver} ]
      then
        ln -sf $jar $(echo $jar | sed "s|-%{version}.jar|-%{javaver}.jar|g")
      fi
      ln -sf $jar $(echo $jar | sed "s|-%{version}.jar|.jar|g")
    done
  popd

  # Install versionless symlinks.
  pushd $RPM_BUILD_ROOT%{_jvmdir}
    ln -sf %{jredir} %{jrelnk}
    ln -sf %{sdkdir} %{sdklnk}
  popd

  pushd $RPM_BUILD_ROOT%{_jvmjardir}
    ln -sf %{sdkdir} %{jrelnk}
    ln -sf %{sdkdir} %{sdklnk}
  popd

  # Remove javaws man page
  rm -f man/man1/javaws*

  # Install man pages.
  install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
  for manpage in man/man1/*
  do
    # Convert man pages to UTF8 encoding.
    iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
    mv -f $manpage.tmp $manpage
    install -m 644 -p $manpage $RPM_BUILD_ROOT%{_mandir}/man1/$(basename \
      $manpage .1)-%{name}.1
  done

  # Install demos and samples.
  cp -a demo $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}
  mkdir -p sample/rmi
  mv bin/java-rmi.cgi sample/rmi
  cp -a sample $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}

popd


# Install nss.cfg
install -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security/


# Install Javadoc documentation.
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}
cp -a %{buildoutputdir}/docs $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# Install icons and menu entries.
for s in 16 24 32 48 ; do
  install -D -p -m 644 \
    openjdk/jdk/src/solaris/classes/sun/awt/X11/java-icon${s}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps/java-%{javaver}.png
done

# Install desktop files.
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
for e in jconsole policytool ; do
    desktop-file-install --vendor=%{name} --mode=644 \
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications $e.desktop
done

# Find JRE directories.
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type d \
  | grep -vE '(jre/lib/security|/demo|/sample)' \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' \
  > %{name}.files-headless
# Find JRE files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type f -o -type l \
  | grep -v jre/lib/security \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  > %{name}.files.all
#split %{name}.files to %{name}.files-headless and %{name}.files
#see https://bugzilla.redhat.com/show_bug.cgi?id=875408
NOT_HEADLESS=\
"%{_jvmdir}/%{jredir}/lib/%{archinstall}/libjsoundalsa.so
%{_jvmdir}/%{jredir}/lib/%{archinstall}/libpulse-java.so
%{_jvmdir}/%{jredir}/lib/%{archinstall}/libsplashscreen.so
%{_jvmdir}/%{jredir}/lib/%{archinstall}/libawt_xawt.so
%{_jvmdir}/%{jredir}/lib/%{archinstall}/libjawt.so
%{_jvmdir}/%{uniquesuffix}/jre/bin/policytool"
#filter %{name}.files from %{name}.files.all to %{name}.files-headless
ALL=`cat %{name}.files.all`
for file in $ALL ; do
    INLCUDE="NO" ;
    for blacklist in $NOT_HEADLESS ; do
    # we can not match normally, because rpmbuild will evaluate !0 result as script failure
    q=`expr match "$file" "$blacklist"` || :
    l=`expr length "$blacklist"` || :
    if [ $q -eq $l ]; then
        INLCUDE="YES" ;
    fi;
done
if [ "x$INLCUDE" = "xNO" ]; then
    echo "$file" >> %{name}.files-headless
else
    echo "$file" >> %{name}.files
fi
done
# Find demo directories.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample -type d \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' \
  > %{name}-demo.files

# FIXME: remove SONAME entries from demo DSOs.  See
# https://bugzilla.redhat.com/show_bug.cgi?id=436497

# Find non-documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep -v README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  >> %{name}-demo.files
# Find documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  | sed 's|^|%doc |' \
  >> %{name}-demo.files

# intentionally after the files generation, as it goes to separate package

%post
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
exit 0

# FIXME: identical binaries are copied, not linked. This needs to be
# fixed upstream.
%post headless
ext=.gz
alternatives \
  --install %{_bindir}/java java %{jrebindir}/java %{priority} \
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{jrelnk} \
  --slave %{_jvmjardir}/jre jre_exports %{_jvmjardir}/%{jrelnk} \
  --slave %{_bindir}/jjs jjs %{jrebindir}/jjs \
  --slave %{_bindir}/keytool keytool %{jrebindir}/keytool \
  --slave %{_bindir}/orbd orbd %{jrebindir}/orbd \
  --slave %{_bindir}/pack200 pack200 %{jrebindir}/pack200 \
  --slave %{_bindir}/rmid rmid %{jrebindir}/rmid \
  --slave %{_bindir}/rmiregistry rmiregistry %{jrebindir}/rmiregistry \
  --slave %{_bindir}/servertool servertool %{jrebindir}/servertool \
  --slave %{_bindir}/tnameserv tnameserv %{jrebindir}/tnameserv \
  --slave %{_bindir}/unpack200 unpack200 %{jrebindir}/unpack200 \
  --slave %{_mandir}/man1/java.1$ext java.1$ext \
  %{_mandir}/man1/java-%{name}.1$ext \
  --slave %{_mandir}/man1/jjs.1$ext jjs.1$ext \
  %{_mandir}/man1/jjs-%{name}.1$ext \
  --slave %{_mandir}/man1/keytool.1$ext keytool.1$ext \
  %{_mandir}/man1/keytool-%{name}.1$ext \
  --slave %{_mandir}/man1/orbd.1$ext orbd.1$ext \
  %{_mandir}/man1/orbd-%{name}.1$ext \
  --slave %{_mandir}/man1/pack200.1$ext pack200.1$ext \
  %{_mandir}/man1/pack200-%{name}.1$ext \
  --slave %{_mandir}/man1/rmid.1$ext rmid.1$ext \
  %{_mandir}/man1/rmid-%{name}.1$ext \
  --slave %{_mandir}/man1/rmiregistry.1$ext rmiregistry.1$ext \
  %{_mandir}/man1/rmiregistry-%{name}.1$ext \
  --slave %{_mandir}/man1/servertool.1$ext servertool.1$ext \
  %{_mandir}/man1/servertool-%{name}.1$ext \
  --slave %{_mandir}/man1/tnameserv.1$ext tnameserv.1$ext \
  %{_mandir}/man1/tnameserv-%{name}.1$ext \
  --slave %{_mandir}/man1/unpack200.1$ext unpack200.1$ext \
  %{_mandir}/man1/unpack200-%{name}.1$ext

alternatives \
  --install %{_jvmdir}/jre-%{origin} \
  jre_%{origin} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{origin} \
  jre_%{origin}_exports %{_jvmjardir}/%{jrelnk}

alternatives \
  --install %{_jvmdir}/jre-%{javaver} \
  jre_%{javaver} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{javaver} \
  jre_%{javaver}_exports %{_jvmjardir}/%{jrelnk}

update-desktop-database %{_datadir}/applications &> /dev/null || :

/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

exit 0

%postun headless
if [ $1 -eq 0 ]
then
  alternatives --remove java %{jrebindir}/java
  alternatives --remove jre_%{origin} %{_jvmdir}/%{jrelnk}
  alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
fi

%post devel
ext=.gz
alternatives \
  --install %{_bindir}/javac javac %{sdkbindir}/javac %{priority} \
  --slave %{_jvmdir}/java java_sdk %{_jvmdir}/%{sdklnk} \
  --slave %{_jvmjardir}/java java_sdk_exports %{_jvmjardir}/%{sdklnk} \
  --slave %{_bindir}/appletviewer appletviewer %{sdkbindir}/appletviewer \
  --slave %{_bindir}/extcheck extcheck %{sdkbindir}/extcheck \
  --slave %{_bindir}/idlj idlj %{sdkbindir}/idlj \
  --slave %{_bindir}/jar jar %{sdkbindir}/jar \
  --slave %{_bindir}/jarsigner jarsigner %{sdkbindir}/jarsigner \
  --slave %{_bindir}/javadoc javadoc %{sdkbindir}/javadoc \
  --slave %{_bindir}/javah javah %{sdkbindir}/javah \
  --slave %{_bindir}/javap javap %{sdkbindir}/javap \
  --slave %{_bindir}/jcmd jcmd %{sdkbindir}/jcmd \
  --slave %{_bindir}/jconsole jconsole %{sdkbindir}/jconsole \
  --slave %{_bindir}/jdb jdb %{sdkbindir}/jdb \
  --slave %{_bindir}/jdeps jdeps %{sdkbindir}/jdeps \
  --slave %{_bindir}/jhat jhat %{sdkbindir}/jhat \
  --slave %{_bindir}/jinfo jinfo %{sdkbindir}/jinfo \
  --slave %{_bindir}/jmap jmap %{sdkbindir}/jmap \
  --slave %{_bindir}/jps jps %{sdkbindir}/jps \
  --slave %{_bindir}/jrunscript jrunscript %{sdkbindir}/jrunscript \
  --slave %{_bindir}/jsadebugd jsadebugd %{sdkbindir}/jsadebugd \
  --slave %{_bindir}/jstack jstack %{sdkbindir}/jstack \
  --slave %{_bindir}/jstat jstat %{sdkbindir}/jstat \
  --slave %{_bindir}/jstatd jstatd %{sdkbindir}/jstatd \
  --slave %{_bindir}/native2ascii native2ascii %{sdkbindir}/native2ascii \
  --slave %{_bindir}/policytool policytool %{sdkbindir}/policytool \
  --slave %{_bindir}/rmic rmic %{sdkbindir}/rmic \
  --slave %{_bindir}/schemagen schemagen %{sdkbindir}/schemagen \
  --slave %{_bindir}/serialver serialver %{sdkbindir}/serialver \
  --slave %{_bindir}/wsgen wsgen %{sdkbindir}/wsgen \
  --slave %{_bindir}/wsimport wsimport %{sdkbindir}/wsimport \
  --slave %{_bindir}/xjc xjc %{sdkbindir}/xjc \
  --slave %{_mandir}/man1/appletviewer.1$ext appletviewer.1$ext \
  %{_mandir}/man1/appletviewer-%{name}.1$ext \
  --slave %{_mandir}/man1/extcheck.1$ext extcheck.1$ext \
  %{_mandir}/man1/extcheck-%{name}.1$ext \
  --slave %{_mandir}/man1/idlj.1$ext idlj.1$ext \
  %{_mandir}/man1/idlj-%{name}.1$ext \
  --slave %{_mandir}/man1/jar.1$ext jar.1$ext \
  %{_mandir}/man1/jar-%{name}.1$ext \
  --slave %{_mandir}/man1/jarsigner.1$ext jarsigner.1$ext \
  %{_mandir}/man1/jarsigner-%{name}.1$ext \
  --slave %{_mandir}/man1/javac.1$ext javac.1$ext \
  %{_mandir}/man1/javac-%{name}.1$ext \
  --slave %{_mandir}/man1/javadoc.1$ext javadoc.1$ext \
  %{_mandir}/man1/javadoc-%{name}.1$ext \
  --slave %{_mandir}/man1/javah.1$ext javah.1$ext \
  %{_mandir}/man1/javah-%{name}.1$ext \
  --slave %{_mandir}/man1/javap.1$ext javap.1$ext \
  %{_mandir}/man1/javap-%{name}.1$ext \
  --slave %{_mandir}/man1/jcmd.1$ext jcmd.1$ext \
  %{_mandir}/man1/jcmd-%{name}.1$ext \
  --slave %{_mandir}/man1/jconsole.1$ext jconsole.1$ext \
  %{_mandir}/man1/jconsole-%{name}.1$ext \
  --slave %{_mandir}/man1/jdb.1$ext jdb.1$ext \
  %{_mandir}/man1/jdb-%{name}.1$ext \
  --slave %{_mandir}/man1/jdeps.1$ext jdeps.1$ext \
  %{_mandir}/man1/jdeps-%{name}.1$ext \
  --slave %{_mandir}/man1/jhat.1$ext jhat.1$ext \
  %{_mandir}/man1/jhat-%{name}.1$ext \
  --slave %{_mandir}/man1/jinfo.1$ext jinfo.1$ext \
  %{_mandir}/man1/jinfo-%{name}.1$ext \
  --slave %{_mandir}/man1/jmap.1$ext jmap.1$ext \
  %{_mandir}/man1/jmap-%{name}.1$ext \
  --slave %{_mandir}/man1/jps.1$ext jps.1$ext \
  %{_mandir}/man1/jps-%{name}.1$ext \
  --slave %{_mandir}/man1/jrunscript.1$ext jrunscript.1$ext \
  %{_mandir}/man1/jrunscript-%{name}.1$ext \
  --slave %{_mandir}/man1/jsadebugd.1$ext jsadebugd.1$ext \
  %{_mandir}/man1/jsadebugd-%{name}.1$ext \
  --slave %{_mandir}/man1/jstack.1$ext jstack.1$ext \
  %{_mandir}/man1/jstack-%{name}.1$ext \
  --slave %{_mandir}/man1/jstat.1$ext jstat.1$ext \
  %{_mandir}/man1/jstat-%{name}.1$ext \
  --slave %{_mandir}/man1/jstatd.1$ext jstatd.1$ext \
  %{_mandir}/man1/jstatd-%{name}.1$ext \
  --slave %{_mandir}/man1/native2ascii.1$ext native2ascii.1$ext \
  %{_mandir}/man1/native2ascii-%{name}.1$ext \
  --slave %{_mandir}/man1/policytool.1$ext policytool.1$ext \
  %{_mandir}/man1/policytool-%{name}.1$ext \
  --slave %{_mandir}/man1/rmic.1$ext rmic.1$ext \
  %{_mandir}/man1/rmic-%{name}.1$ext \
  --slave %{_mandir}/man1/schemagen.1$ext schemagen.1$ext \
  %{_mandir}/man1/schemagen-%{name}.1$ext \
  --slave %{_mandir}/man1/serialver.1$ext serialver.1$ext \
  %{_mandir}/man1/serialver-%{name}.1$ext \
  --slave %{_mandir}/man1/wsgen.1$ext wsgen.1$ext \
  %{_mandir}/man1/wsgen-%{name}.1$ext \
  --slave %{_mandir}/man1/wsimport.1$ext wsimport.1$ext \
  %{_mandir}/man1/wsimport-%{name}.1$ext \
  --slave %{_mandir}/man1/xjc.1$ext xjc.1$ext \
  %{_mandir}/man1/xjc-%{name}.1$ext

alternatives \
  --install %{_jvmdir}/java-%{origin} \
  java_sdk_%{origin} %{_jvmdir}/%{sdklnk} %{priority} \
  --slave %{_jvmjardir}/java-%{origin} \
  java_sdk_%{origin}_exports %{_jvmjardir}/%{sdklnk}

alternatives \
  --install %{_jvmdir}/java-%{javaver} \
  java_sdk_%{javaver} %{_jvmdir}/%{sdklnk} %{priority} \
  --slave %{_jvmjardir}/java-%{javaver} \
  java_sdk_%{javaver}_exports %{_jvmjardir}/%{sdklnk}

update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

exit 0

%postun devel
if [ $1 -eq 0 ]
then
  alternatives --remove javac %{sdkbindir}/javac
  alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdklnk}
  alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdklnk}
fi

exit 0

%post javadoc
alternatives \
  --install %{_javadocdir}/java javadocdir %{_javadocdir}/%{name}/api \
  %{priority}

exit 0

%postun javadoc
if [ $1 -eq 0 ]
then
  alternatives --remove javadocdir %{_javadocdir}/%{name}/api
fi

exit 0


%files -f %{name}.files
%{_datadir}/icons/hicolor/*x*/apps/java-%{javaver}.png


%files headless -f %{name}.files-headless
%defattr(-,root,root,-)
%doc %{buildoutputdir}/images/j2sdk-image/jre/ASSEMBLY_EXCEPTION
%doc %{buildoutputdir}/images/j2sdk-image/jre/LICENSE
%doc %{buildoutputdir}/images/j2sdk-image/jre/THIRD_PARTY_README

%dir %{_jvmdir}/%{sdkdir}
%exclude %{_jvmdir}/%{sdkdir}/src.zip
%{_jvmdir}/%{jrelnk}
%{_jvmjardir}/%{jrelnk}
%{jvmjardir}
%dir %{_jvmdir}/%{jredir}/lib/security
%{_jvmdir}/%{jredir}/lib/security/cacerts
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.policy
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.security
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/blacklisted.certs
%{_mandir}/man1/java-%{name}.1*
%{_mandir}/man1/jjs-%{name}.1*
%{_mandir}/man1/keytool-%{name}.1*
%{_mandir}/man1/orbd-%{name}.1*
%{_mandir}/man1/pack200-%{name}.1*
%{_mandir}/man1/rmid-%{name}.1*
%{_mandir}/man1/rmiregistry-%{name}.1*
%{_mandir}/man1/servertool-%{name}.1*
%{_mandir}/man1/tnameserv-%{name}.1*
%{_mandir}/man1/unpack200-%{name}.1*
%{_jvmdir}/%{jredir}/lib/security/nss.cfg
%{_jvmdir}/%{jredir}/lib/security/policy

%files devel
%defattr(-,root,root,-)
%doc %{buildoutputdir}/images/j2sdk-image/ASSEMBLY_EXCEPTION
%doc %{buildoutputdir}/images/j2sdk-image/LICENSE
%doc %{buildoutputdir}/images/j2sdk-image/THIRD_PARTY_README
%dir %{_jvmdir}/%{sdkdir}/bin
%dir %{_jvmdir}/%{sdkdir}/include
%dir %{_jvmdir}/%{sdkdir}/lib
%if %{with_systemtap}
%dir %{_jvmdir}/%{sdkdir}/tapset
%endif
%{_jvmdir}/%{sdkdir}/bin/*
%{_jvmdir}/%{sdkdir}/include/*
%{_jvmdir}/%{sdkdir}/lib/*
%if %{with_systemtap}
%{_jvmdir}/%{sdkdir}/tapset/*.stp
%endif
%{_jvmdir}/%{sdklnk}
%{_jvmjardir}/%{sdklnk}
%{_datadir}/applications/*jconsole.desktop
%{_datadir}/applications/*policytool.desktop
%{_mandir}/man1/appletviewer-%{name}.1*
%{_mandir}/man1/extcheck-%{name}.1*
%{_mandir}/man1/idlj-%{name}.1*
%{_mandir}/man1/jar-%{name}.1*
%{_mandir}/man1/jarsigner-%{name}.1*
%{_mandir}/man1/javac-%{name}.1*
%{_mandir}/man1/javadoc-%{name}.1*
%{_mandir}/man1/javah-%{name}.1*
%{_mandir}/man1/javap-%{name}.1*
%{_mandir}/man1/jconsole-%{name}.1*
%{_mandir}/man1/jcmd-%{name}.1*
%{_mandir}/man1/jdb-%{name}.1*
%{_mandir}/man1/jdeps-%{name}.1*
%{_mandir}/man1/jhat-%{name}.1*
%{_mandir}/man1/jinfo-%{name}.1*
%{_mandir}/man1/jmap-%{name}.1*
%{_mandir}/man1/jps-%{name}.1*
%{_mandir}/man1/jrunscript-%{name}.1*
%{_mandir}/man1/jsadebugd-%{name}.1*
%{_mandir}/man1/jstack-%{name}.1*
%{_mandir}/man1/jstat-%{name}.1*
%{_mandir}/man1/jstatd-%{name}.1*
%{_mandir}/man1/native2ascii-%{name}.1*
%{_mandir}/man1/policytool-%{name}.1*
%{_mandir}/man1/rmic-%{name}.1*
%{_mandir}/man1/schemagen-%{name}.1*
%{_mandir}/man1/serialver-%{name}.1*
%{_mandir}/man1/wsgen-%{name}.1*
%{_mandir}/man1/wsimport-%{name}.1*
%{_mandir}/man1/xjc-%{name}.1*
%if %{with_systemtap}
%{tapsetroot}/tapset/*/*.stp
%endif

%files demo -f %{name}-demo.files
%defattr(-,root,root,-)
%doc %{buildoutputdir}/images/j2sdk-image/jre/LICENSE

%files src
%defattr(-,root,root,-)
%doc README.src
%{_jvmdir}/%{sdkdir}/src.zip

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}
%doc %{buildoutputdir}/images/j2sdk-image/jre/LICENSE
