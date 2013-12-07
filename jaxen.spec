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

Summary:	An XPath engine written in Java
Name:		jaxen
Version:	1.1.2
Release:	5
License:	BSD
Url:		http://jaxen.codehaus.org/
Group:		Development/Java
Source0:	http://dist.codehaus.org/jaxen/distributions/jaxen-1.1.2.tar.gz
Source6:	http://prdownloads.sourceforge.net/dom4j/dom4j-%{dom4jver}.tar.gz
Source7:	build.xml
%if %with maven
Source1:	pom-maven2jpp-depcat.xsl
Source2:	pom-maven2jpp-newdepmap.xsl
Source3:	pom-maven2jpp-mapdeps.xsl
Source4:	jaxen-1.1-b7-jpp-depmap.xml
Source5:	jaxen-1.1-b7-build.xml
%endif
Patch0:	%{name}-notest.patch
%if !%{gcj_support}
BuildArch:	noarch
BuildRequires:	java-devel >= 0:1.4.2
%else
BuildRequires:	java-gcj-compat-devel
%endif
BuildRequires:	ant >= 0:1.6
BuildRequires:	ant-junit
BuildRequires:	java-rpmbuild >= 0:1.6
BuildRequires:	junit
%if %with maven
BuildRequires:	maven >= 0:1.1 saxon saxon-scripts
BuildRequires:	maven-plugin-changes >= 0:1.1
BuildRequires:	maven-plugin-file-activity >= 0:1.1
BuildRequires:	maven-plugin-developer-activity >= 0:1.1
BuildRequires:	maven-plugin-license >= 0:1.1
BuildRequires:	maven-plugin-jdepend >= 0:1.1
BuildRequires:	maven-plugin-tasklist >= 0:1.1
%endif
%if %without bootstrap
BuildRequires:	dom4j >= 0:1.6.1
%endif
BuildRequires:	jdom >= 0:1.0-0.rc1.1jpp
BuildRequires:	xalan-j2
BuildRequires:	xerces-j2
BuildRequires:	xom
%if %without bootstrap
Requires:	dom4j >= 0:1.6.1
%endif
Requires:	jdom >= 0:1.0-0.rc1.1jpp
Requires:	xalan-j2
Requires:	xerces-j2
Requires:	xom
%rename		jaxen-bootstrap

%description
Jaxen is an XPath engine written in Java to work against a variety of XML
based object models such as DOM, dom4j and JDOM together with Java
Beans.

%if %with maven
%if %with manual
%package manual
Summary:	Documents for %{name}
Group:		Development/Java

%description manual
%{summary}.
%endif
%endif

%package demo
Summary:	Samples for %{name}
Group:		Development/Java
Requires:	jaxen = %{epoch}:%{version}-%{release}

%description demo
%{summary}.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

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
%ant -Dnoget=true jar javadoc
%endif

%install

# jars
install -d -m 755 %{buildroot}%{_javadir}
install -m 644 target/%{name}-%{version}.jar \
%{buildroot}%{_javadir}/%{name}-%{version}.jar

(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do \
ln -sf ${jar} ${jar/-%{version}/}; done)

# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
%if %with maven
cp -pr target/docs/apidocs/* %{buildroot}%{_javadocdir}/%{name}-%{version}
rm -rf target/docs/apidocs
%else
cp -pr dist/docs/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%endif
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

# manual
%if %with maven
%if %with manual
install -d -m 755 %{buildroot}%{_docdir}/%{name}-%{version}
cp -pr target/docs/* %{buildroot}%{_docdir}/%{name}-%{version}
%endif
%endif

# demo
install -d -m 755 %{buildroot}%{_datadir}/%{name}-%{version}/samples
cp -pr src/java/samples/* %{buildroot}%{_datadir}/%{name}-%{version}/samples

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%files
%doc LICENSE.txt
%{_javadir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%if %with maven
%if %with manual
%files manual
%doc %{_docdir}/%{name}-%{version}
%endif
%endif

%files javadoc
%doc %{_javadocdir}/*

%files demo
%{_datadir}/%{name}-%{version}

