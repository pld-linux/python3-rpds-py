#
# Conditional build:
%bcond_without	doc	# API documentation
%bcond_without	tests	# unit tests

%define		module	rpds-py
Summary:	Python bindings to Rust's persistent data structures (rpds)
Summary(pl.UTF-8):	Wiązania Pythona do rustowych trwałych struktur danych (rpds)
Name:		python3-%{module}
Version:	0.26.0
Release:	1
License:	MIT
Group:		Libraries/Python
#Source0Download: https://pypi.org/simple/rpds-py/
Source0:	https://files.pythonhosted.org/packages/source/r/rpds-py/rpds_py-%{version}.tar.gz
# Source0-md5:	08ebed346f6d749762503b885ef18164
# cargo vendor-filterer --platform='*-unknown-linux-*' --tier=2
# tar cJf rpds_py-crates-%{version}.tar.xz vendor Cargo.lock
Source1:	rpds_py-crates-%{version}.tar.xz
# Source1-md5:	5c9334e893a34348c3d13fa06e5bed60
URL:		https://pypi.org/project/rpds-py/
BuildRequires:	cargo
BuildRequires:	python3-build
BuildRequires:	python3-installer
BuildRequires:	python3-maturin >= 1.9
BuildRequires:	python3-maturin < 2
BuildRequires:	python3-modules >= 1:3.9
# latest version from vendored crates - main Cargo.toml doesn't specify rust-version
BuildRequires:	rust >= 1.85.0
%if %{with tests}
BuildRequires:	python3-pytest
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.044
%if %{with doc}
BuildRequires:	python3-furo
BuildRequires:	python3-pygments-github-lexers
BuildRequires:	python3-sphinx_copybutton
BuildRequires:	python3-sphinxcontrib-spelling > 5
BuildRequires:	python3-sphinxext.opengraph
BuildRequires:	python3-url-py
BuildRequires:	sphinx-pdg-3 > 5
%endif
Requires:	python3-modules >= 1:3.9
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Python bindings to the Rust rpds crate for persistent data structures.

%description -l pl.UTF-8
Wiązania Pythona do paki Rusta rpds do trwałych struktur danych.

%package apidocs
Summary:	API documentation for Python %{module} module
Summary(pl.UTF-8):	Dokumentacja API modułu Pythona %{module}
Group:		Documentation

%description apidocs
API documentation for Python %{module} module.

%description apidocs -l pl.UTF-8
Dokumentacja API modułu Pythona %{module}.

%prep
%setup -q -n rpds_py-%{version} -a1

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config.toml <<EOF
[source.crates-io]
#registry = 'https://github.com/rust-lang/crates.io-index'
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

%if %{with tests} || %{with doc}
%{__python3} -m zipfile -e build-3/*.whl build-3-ext
%endif

%if %{with tests}
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
%{__python3} -m pytest -o pythonpath="$PWD/build-3-ext" tests
%endif

%if %{with doc}
PYTHONPATH=$(pwd)/build-3-ext \
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
%doc docs/_build/html/{_static,*.html,*.js}
%endif
