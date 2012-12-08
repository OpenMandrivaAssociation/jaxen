# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support 1

%bcond_without     bootstrap
%define dom4jver   1.6.1

# We don't want to build with maven
%bcond_with        maven

# If you don't want the manual to be built, give rpmbuild option
# '--without manual'
%bcond_with        manual

Name:           jaxen
Version:        1.1.2
Release:        %mkrel 1.3
Epoch:          0
Summary:        An XPath engine written in Java
License:        BSD
Url:            http://jaxen.codehaus.org/
Group:          Development/Java
Source0:        http://dist.codehaus.org/jaxen/distributions/jaxen-1.1.2.tar.gz
Source6:        http://prdownloads.sourceforge.net/dom4j/dom4j-%{dom4jver}.tar.gz
Source7:        build.xml
%if %with maven
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        jaxen-1.1-b7-jpp-depmap.xml

Source5:        jaxen-1.1-b7-build.xml
%endif
Patch0:         %{name}-notest.patch
%if %without bootstrap
Requires:       dom4j >= 0:1.6.1
%endif
Requires:       jdom >= 0:1.0-0.rc1.1jpp
Requires:       xalan-j2
Requires:       xerces-j2
Requires:       xom
BuildRequires:  ant >= 0:1.6, java-rpmbuild >= 0:1.6, junit, ant-junit
BuildRequires:  java-devel
%if %with maven
BuildRequires:  maven >= 0:1.1, saxon, saxon-scripts
BuildRequires:  maven-plugin-changes >= 0:1.1
BuildRequires:  maven-plugin-file-activity >= 0:1.1
BuildRequires:  maven-plugin-developer-activity >= 0:1.1
BuildRequires:  maven-plugin-license >= 0:1.1
BuildRequires:  maven-plugin-jdepend >= 0:1.1
BuildRequires:  maven-plugin-tasklist >= 0:1.1
%endif
%if %without bootstrap
BuildRequires:  dom4j >= 0:1.6.1
%endif
BuildRequires:  jdom >= 0:1.0-0.rc1.1jpp
BuildRequires:  xalan-j2
BuildRequires:  xerces-j2
BuildRequires:  xom
Provides:       jaxen-bootstrap <= %{version}-%{release}
Obsoletes:      jaxen-bootstrap <= %{version}-%{release}
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
BuildRequires:  java-devel >= 0:1.4.2
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Jaxen is an XPath engine written in Java to work against a variety of XML
based object models such as DOM, dom4j and JDOM together with Java
Beans.

%if %with maven
%if %with manual
%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.
%endif
%endif

%package demo
Summary:        Samples for %{name}
Group:          Development/Java
Requires:       jaxen = %{epoch}:%{version}-%{release}

%description demo
%{summary}.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%prep
# If you dont want to build with maven, give rpmbuild option '--without
# maven'
# If you dont want the manual to be built, give rpmbuild option
# '--without manual'

%if %without bootstrap
%setup -q -a 7
%else
%setup -q -a 6
%patch0
%endif
%{_bindir}/find . -name "*.jar" | %{_bindir}/xargs -t %{__rm}

%if %with maven
export DEPCAT=$(pwd)/jaxen-1.1-b7-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > jaxen-1.1-b7-depmap.new.xml
%else
%if %without bootstrap
mkdir -p target/lib
pushd target/lib
build-jar-repository . dom4j-1.6.1.jar jdom-1.0.jar xom-1.0.jar
ln -s %{_javadir}/xerces-j2.jar xercesImpl-2.6.2.jar
popd
%endif
%endif

%build
%if %with maven
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    cp project.xml project.xml.orig
    /usr/bin/saxon -o project.xml project.xml.orig %{SOURCE3} map=%{SOURCE4}
    popd
done

mkdir .maven

%if %with manual
maven \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=$(pwd)/.maven \
        jar javadoc xdoc
%else
maven \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=$(pwd)/.maven \
        jar javadoc
%endif
%else
%if %with bootstrap
export CLASSPATH=$(build-classpath \
jdom \
xalan-j2 \
xerces-j2 \
xom \
)
pushd dom4j-%{dom4jver}/src/java
javac -sourcepath ../../../src/java/main:. \
        org/dom4j/Attribute.java \
        org/dom4j/Branch.java \
        org/dom4j/CDATA.java \
        org/dom4j/Comment.java \
        org/dom4j/Document.java \
        org/dom4j/DocumentException.java \
        org/dom4j/Element.java \
        org/dom4j/Namespace.java \
        org/dom4j/Node.java \
        org/dom4j/ProcessingInstruction.java \
        org/dom4j/Text.java \
        org/dom4j/io/SAXReader.java

%{jar} cf ../../dom4j.jar $(find . -name "*.class")
popd

export CLASSPATH=$(build-classpath \
jdom \
xalan-j2 \
xerces-j2 \
xom \
):`pwd`/dom4j-%{dom4jver}/dom4j.jar
%endif
%{ant} -Dnoget=true jar javadoc
%endif

%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 target/%{name}-%{version}.jar \
$RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do \
ln -sf ${jar} ${jar/-%{version}/}; done)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %with maven
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
rm -rf target/docs/apidocs
%else
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# manual
%if %with maven
%if %with manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -pr target/docs/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
%endif
%endif

# demo
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}-%{version}/samples
cp -pr src/java/samples/* $RPM_BUILD_ROOT%{_datadir}/%{name}-%{version}/samples

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644,root,root,0755)
%doc LICENSE.txt
%{_javadir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%if %with maven
%if %with manual
%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}
%endif
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/*

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}-%{version}


%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0:1.1.2-1.3mdv2011.0
+ Revision: 665819
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.1.2-1.2mdv2011.0
+ Revision: 606075
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.1.2-1.1mdv2010.1
+ Revision: 523068
- rebuilt for 2010.1

* Wed Feb 18 2009 Jérôme Soyer <saispo@mandriva.org> 0:1.1.2-1.0mdv2009.1
+ Revision: 342367
- New upstream release
- New upstream release

* Fri Dec 21 2007 Olivier Blin <oblin@mandriva.com> 0:1.1.1-1.4mdv2009.0
+ Revision: 136503
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:1.1.1-1.4mdv2008.1
+ Revision: 120932
- buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:1.1.1-1.3mdv2008.0
+ Revision: 87427
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Sun Sep 09 2007 Pascal Terjan <pterjan@mandriva.org> 0:1.1.1-1.2mdv2008.0
+ Revision: 82794
- update to new version

* Thu May 17 2007 David Walluck <walluck@mandriva.org> 0:1.1.1-1.1mdv2008.0
+ Revision: 27665
- 1.1.1

* Mon Apr 23 2007 David Walluck <walluck@mandriva.org> 0:1.1-1.2.1mdv2008.0
+ Revision: 17680
- Import jaxen



* Mon Apr 23 2007 David Walluck <walluck@mandriva.org> 0:1.1-1.2.1mdv2008.0
- release

* Tue Feb 20 2007 Vivek Lakshmanan <vivekl@redhat.com> 0:1.1-1jpp.2.fc7
- Add build-requires on ant-junit

* Mon Feb 19 2007 Andrew Overholt <overholt@redhat.com> 0:1.1-1jpp.1
- Add explicit version-release on Provides and Obsoletes
- Untabify
- Remove %%ghost on versioned javadoc dir
- Just include %%{_javadocdir}/* for javadoc package

* Wed Feb 14 2007 Andrew Overholt <overholt@redhat.com> 0:1.1-1jpp.1
- Bump to 1.1 final
- Make release Xjpp.Y%%{?dist}
- Remove Distribution, Vendor
- Fix Group
- Remove cleaning of buildroot from beginning of %%prep
- Add cleaning of buildroot to beginning of %%install
- Remove %%section free
- Use Fedora buildroot

* Sun Feb 26 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.1-0.b7.4jpp
- Rebuild for JPP 1.7

* Wed Feb 15 2006 Ralph Apel <r.apel@r-apel.de> 0:1.1-0.b7.3jpp
- Insert Copyright notice

* Mon Feb 13 2006 Ralph Apel <r.apel@r-apel.de> 0:1.1-0.b7.2jpp
- Adapt to maven-1.1
- Create option to build without maven

* Wed Aug 17 2005 Ralph Apel <r.apel@r-apel.de> 0:1.1-0.b7.1jpp
- Upgrade to 1.1-beta-7
- Now mavenized
- Requiring dom4j >= 1.6.1
- rpmbuild option to inhibit build of manual (needs newer maven)

* Thu Sep 09 2004 Ralph Apel <r.apel@r-apel.de> 0:1.1-0.b2.1jpp
- Upgrade to 1.1-beta-2
- Drop saxpath requirement as saxpath is now included in jaxen

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:1.0-4jpp
- Rebuild with ant-1.6.2
* Mon Jan 19 2004 Ralph Apel <r.apel@r-apel.de> 0:1.0-3jpp
- build against dom4j-1.4-1jpp
- introduce manual and demo subpackages
- patch org.jaxen.dom4j.DocumentNavigatorTest
- include LICENSE in main package
- run tests during build

* Thu Jan 15 2004 Ralph Apel <r.apel@r-apel.de> 0:1.0-2jpp
- activate support for dom4j by renaming lib/dom4j-core.jar to .zip

* Sun May 04 2003 David Walluck <david@anti-microsoft.org> 0:1.0-1jpp
- release
