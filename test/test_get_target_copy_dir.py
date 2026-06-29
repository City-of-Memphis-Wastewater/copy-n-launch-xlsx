#
from __future__ import annotations

def test_get_target_copy_dir_func():
    from copy_n_launch_xlsx.paths import get_target_copy_dir
    path = get_target_copy_dir()
    print(path)
