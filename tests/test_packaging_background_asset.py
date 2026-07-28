import subprocess
import sys
import zipfile
from pathlib import Path


def test_wheel_includes_visual_assets(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(tmp_path),
            str(repo_root),
        ],
        check=True,
    )

    wheel_paths = list(tmp_path.glob("*.whl"))
    assert len(wheel_paths) == 1

    with zipfile.ZipFile(wheel_paths[0]) as wheel_zip:
        assert (
            "ant_colony/assets/backgrounds/old-growth-forest-map.png"
            in wheel_zip.namelist()
        )
        assert (
            "ant_colony/assets/ants/meadow-ant-worker-2x2.png" in wheel_zip.namelist()
        )
