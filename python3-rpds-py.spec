# Conditional build:
%bcond_without	doc	# API documentation
%bcond_without	tests	# unit tests

%define		module	rpds-py
Summary:	Python bindings to Rust's persistent data structures (rpds)
Name:		python3-%{module}
Version:	0.24.0
Release:	1
License:	MIT
Group:		Libraries/Python
#Source0Download: https://pypi.org/simple/rpds-py/
Source0:	https://files.pythonhosted.org/packages/source/r/rpds-py/rpds_py-%{version}.tar.gz
# Source0-md5:	19e64c8eb9c1ea9123ba570470744b8f
# cargo vendor
# tar cJf python3-rpds-py-crates-%{version}.tar.xz vendor Cargo.lock
Source1:	%{name}-crates-%{version}.tar.xz
# Source1-md5:	e993d7c5fda821ef56d9a0851b3ff552
URL:		https://pypi.org/project/rpds-py/
BuildRequires:	cargo
BuildRequires:	python3-build
BuildRequires:	python3-installer
BuildRequires:	python3-maturin
BuildRequires:	python3-modules >= 1:3.2
BuildRequires:	rust
%if %{with tests}
BuildRequires:	python3-pytest
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.044
%if %{with doc}
BuildRequires:	python3-url
BuildRequires:	sphinx-pdg-3
%endif
Requires:	python3-modules >= 1:3.2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Python bindings to the Rust rpds crate for persistent data structures.

%package apidocs
Summary:	API documentation for Python %{module} module
Summary(pl.UTF-8):	Dokumentacja API modułu Pythona %{module}
Group:		Documentation

%description apidocs
API documentation for Python %{module} module.

%description apidocs -l pl.UTF-8
Dokumentacja API modułu Pythona %{module}.

%prep
%setup -q -a1 -n rpds_py-%{version}

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/src/rust/.cargo"
export CARGO_OFFLINE=true
export RUSTFLAGS="%{rpmrustflags}"
export CARGO_TERM_VERBOSE=true
%ifarch x32
export CARGO_BUILD_TARGET=x86_64-unknown-linux-gnux32
export PKG_CONFIG_ALLOW_CROSS=1
export PYO3_CROSS_LIB_DIR=%{_libdir}
%endif

export CFLAGS="%{rpmcflags}"

%py3_build_pyproject

%if %{with tests}
%{__python3} -m zipfile -e build-3/*.whl build-3-test
# use explicit plugins list for reliable builds (delete PYTEST_PLUGINS if empty)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS= \
%{__python3} -m pytest -o pythonpath="$PWD/build-3-test" tests
%endif

%if %{with doc}
sphinx-build-3 -b html docs docs/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%py3_install_pyproject

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE README.rst
%dir %{py3_sitedir}/rpds
%{py3_sitedir}/rpds/*.py
%{py3_sitedir}/rpds/*.pyi
%{py3_sitedir}/rpds/py.typed
%attr(755,root,root) %{py3_sitedir}/rpds/rpds.cpython-*.so
%{py3_sitedir}/rpds/__pycache__
%{py3_sitedir}/rpds_py-%{version}.dist-info

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/*
%endif
