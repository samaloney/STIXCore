import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest
from stixcore.idb.idb import IDB
from stixcore.idb.manager import IdbManager


@pytest.fixture
def idbManager():
    return IdbManager(Path(os.path.abspath(__file__)).parent / 'data')

def teardown_function():
    downloadtest = Path(os.path.abspath(__file__)).parent / 'data/v2.26.33'
    if downloadtest.exists():
        shutil.rmtree(str(downloadtest))

def test_idbManager(idbManager):
    assert str(idbManager.data_root) == str((Path(os.path.abspath(__file__)).parent / 'data'))

def test_root_not_found_error():
    with pytest.raises(ValueError) as e:
        _ = IdbManager(".foo/")
    assert str(e.value).startswith('path not found')

@pytest.mark.parametrize('versions', [("2.26.1",False),("2.26.2",False),((2, 26, 3),False),("2.26.34",True),("1.2.3",False)])
def test_has_version(versions, idbManager):
    versionlabel, should = versions
    hasV = idbManager.has_version(versionlabel)
    assert should == hasV


@pytest.mark.remote_data
def test_download_version(idbManager):
    assert idbManager.download_version("2.26.33")

    with pytest.raises(ValueError) as e:
        idbManager.download_version("2.26.33")
    assert len(str(e.value)) > 1

    assert idbManager.download_version("2.26.33", force=True)

def test_find_version(idbManager):
    idb = idbManager.get_idb(utc=datetime(2020,6,6))
    assert idb.get_idb_version() == "2.26.34"
    idb.close()

    with pytest.raises(ValueError) as e:
        idb = idbManager.get_idb(utc=datetime(2019,6,6))
        assert idb.get_idb_version() == "2.26.34"
        idb.close()
    assert len(str(e.value)) > 1

    with pytest.raises(ValueError) as e:
        idb = idbManager.get_idb(utc=datetime(2018,6,6))
        assert idb.get_idb_version() == "2.26.34"
        idb.close()
    assert len(str(e.value)) > 1

    v = idbManager.find_version(utc=None)
    assert v == "2.26.3"

def test_get_versions(idbManager):
    versions = idbManager.get_versions()
    assert isinstance(versions, list)
    #just 3 not 4 as 2.26.2 contains no file
    assert len(versions) == 3

def test_get_idb_not_found_error(idbManager):
    with pytest.raises(ValueError) as e:
        _ = idbManager.get_idb("a.b.c")
    assert str(e.value).startswith('Version')

def test_get_idb(idbManager):
    idb = idbManager.get_idb("2.26.34")
    assert idb.get_idb_version() == "2.26.34"
    assert idb.is_connected() == True
    idb.close()
    assert idb.is_connected() == False