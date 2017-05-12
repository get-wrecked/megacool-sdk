import sys
import pytest

sys.path.insert(0, 'tools')

from release_android import Version


@pytest.mark.parametrize('smaller_version,larger_version', (
    (Version(2, 0, 0, ''), Version(2, 0, 1, '')),
    (Version(1, 0, 0, ''), Version(2, 0, 0, '')),
    (Version(1, 0, 0, 'rc1'), Version(1, 0, 0, '')),
    (Version(1, 0, 0, 'rc1'), Version(1, 0, 0, 'rc2')),
))
def test_version_ordering_unequal(larger_version, smaller_version):
    assert smaller_version < larger_version
    assert larger_version > smaller_version
    assert smaller_version != larger_version
