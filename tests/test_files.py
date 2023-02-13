import os

import utils.files as files


def test_change_directory(tmpdir):
    cwd = os.getcwd()
    nwd = tmpdir.mkdir("temp")
    with files.ChangeDirectory(nwd):
        assert os.getcwd() == nwd
    assert os.getcwd() == cwd
