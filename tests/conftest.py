# nflprojections/tests/conftest.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

from pathlib import Path
import sys

import pytest

sys.path.append("../nflprojections")


@pytest.fixture(scope="session", autouse=True)
def base_directory(request):
    """Gets 'basedir' directory with test datafiles"""
    return Path(request.config.rootdir) / "tests/testdata/2020/6"


@pytest.fixture(scope="session", autouse=True)
def root_directory(request):
    """Gets root directory"""
    return Path(request.config.rootdir)


@pytest.fixture(scope="session", autouse=True)
def test_directory(request):
    """Gets root directory of tests"""
    return Path(request.config.rootdir) / "tests"


@pytest.fixture(scope="session", autouse=True)
def raw_directory(request):
    """Gets 'raw' directory with test datafiles"""
    return Path(request.config.rootdir) / "tests/testdata/2020/6/raw"


@pytest.fixture()
def tprint(request, capsys):
    """Fixture for printing info after test, not supressed by pytest stdout/stderr capture"""
    lines = []
    yield lines.append

    with capsys.disabled():
        for line in lines:
            sys.stdout.write("\n{}".format(line))

