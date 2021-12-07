"""Test that setuptools-scm is working correctly"""
import diatherm

def test_version():
    """Check that the version is not None"""
    assert diatherm.__version__ is not None
