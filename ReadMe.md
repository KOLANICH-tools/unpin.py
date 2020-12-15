unpin.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
=========
~~[wheel (GitLab)](https://gitlab.com/KOLANICH-tools/unpin.py/-/jobs/artifacts/master/raw/dist/unpin-0.CI-py3-none-any.whl?job=build)~~
[wheel (GHA via `nightly.link`)](https://nightly.link/KOLANICH-tools/unpin.py/workflows/CI/master/unpin-0.CI-py3-none-any.whl)
~~![GitLab Build Status](https://gitlab.com/KOLANICH-tools/unpin.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH-tools/unpin.py/badges/master/coverage.svg)~~
[![GitHub Actions](https://github.com/KOLANICH-tools/unpin.py/workflows/CI/badge.svg)](https://github.com/KOLANICH-tools/unpin.py/actions/)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH-tools/unpin.py.svg)](https://libraries.io/github/KOLANICH-tools/unpin.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://github.com/KOLANICH-tools/antiflash.py)

A tool to remove harmful versions pinnings from prebuilt wheels.

ToDo: **Currently `libzip` is used for updating files witin the archive. It doesn't allow rewriting files in archives without creating a copy of the archive. [It is considered contradicting `libzip` goals by its authors.](https://github.com/nih-at/libzip/issues/304)**. We need a lib allowing to do that.

## How to use

```bash
unpin ./tf_nightly-2.10.0.dev20220617-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

will output the report, for which the harmful constraints have been altered. `-` means "removed".

```
gast (>=0.2.1)
	- <=0.4.0
grpcio (>=1.24.3)
	- <2.0
keras-nightly
	- ~=2.10.0.dev
protobuf (>=3.9.2)
	- <3.20
tb-nightly
	- ~=2.10.0.a
tf-estimator-nightly
	- ~=2.10.0.dev
```

```bash
unpin ./requests-2.28.1.dev0+gda9996fe-py3-none-any.whl
```

```
charset-normalizer 
	- ~=2.0.0
idna (>=2.5) 
	- <4
urllib3 (>=1.21.1) 
	- <1.27
PySocks (>=1.5.6) ; extra == 'socks'
	- !=1.5.7
chardet (>=3.0.2) ; extra == 'use_chardet_on_py3'
	- <5
```
