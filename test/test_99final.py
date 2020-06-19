import os
import shutil
import falcon

from . import client

def test_final(client):
    if os.path.isdir("test/codes"):
        shutil.rmtree("test/codes")
    if os.path.isdir("test/images"):
        shutil.rmtree("test/images")